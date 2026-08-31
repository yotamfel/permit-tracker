"""
Public, no-login "click to respond" endpoints for post_release_feedback
(spec addendum: Post-Release Feedback + Homepage Calendar, §1.2). These render
plain HTML directly - there's no SPA route for this, on purpose, to keep the
email-click flow as low-friction as possible.
"""
from datetime import datetime, timezone
from html import escape

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.destination import Destination
from app.models.post_release_feedback import PostReleaseFeedback

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


def _get_or_404(db: Session, token: str) -> PostReleaseFeedback:
    fb = db.query(PostReleaseFeedback).filter(PostReleaseFeedback.response_token == token).first()
    if fb is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return fb


def _render(fb: PostReleaseFeedback, destination_name: str) -> str:
    base = f"/api/feedback/{fb.response_token}"

    def yesno_links(question: str, param: str, current: bool | None) -> str:
        if current is not None:
            return f"<p>{question} <strong>{'Yes' if current else 'No'}</strong></p>"
        return (
            f"<p>{question}<br/>"
            f'<a href="{base}/answer?{param}=true">Yes</a> &nbsp;|&nbsp; '
            f'<a href="{base}/answer?{param}=false">No</a></p>'
        )

    comment_block = (
        f"<p>Your comment: {escape(fb.free_text_comment)}</p>"
        if fb.free_text_comment
        else (
            f'<form method="post" action="{base}/comment">'
            '<textarea name="comment" rows="3" style="width:100%;max-width:400px" '
            'placeholder="Anything else you want to tell us? (optional)"></textarea><br/>'
            '<button type="submit">Send comment</button></form>'
        )
    )

    return f"""
    <html>
    <head><meta charset="utf-8"><title>Thanks for the feedback</title></head>
    <body style="font-family:sans-serif;max-width:480px;margin:40px auto;line-height:1.5">
      <h2>Thanks for letting us know about {escape(destination_name)}!</h2>
      {yesno_links("Did you get in?", "succeeded", fb.succeeded)}
      {yesno_links("Did Permit Tracker help you prepare?", "found_site_helpful", fb.found_site_helpful)}
      {comment_block}
    </body>
    </html>
    """


@router.get("/{token}", response_class=HTMLResponse)
def view_feedback(token: str, db: Session = Depends(get_db)) -> HTMLResponse:
    fb = _get_or_404(db, token)
    d = db.get(Destination, fb.destination_id)
    return HTMLResponse(_render(fb, d.name if d else "your destination"))


@router.get("/{token}/answer")
def answer_feedback(
    token: str, succeeded: bool | None = None, found_site_helpful: bool | None = None, db: Session = Depends(get_db)
) -> RedirectResponse:
    fb = _get_or_404(db, token)
    if succeeded is not None:
        fb.succeeded = succeeded
    if found_site_helpful is not None:
        fb.found_site_helpful = found_site_helpful
    fb.responded_at = datetime.now(timezone.utc)
    db.add(fb)
    db.commit()
    return RedirectResponse(url=f"/api/feedback/{token}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{token}/comment")
def comment_feedback(token: str, comment: str = Form(...), db: Session = Depends(get_db)) -> RedirectResponse:
    fb = _get_or_404(db, token)
    fb.free_text_comment = comment.strip()[:2000]
    fb.responded_at = datetime.now(timezone.utc)
    db.add(fb)
    db.commit()
    return RedirectResponse(url=f"/api/feedback/{token}", status_code=status.HTTP_303_SEE_OTHER)
