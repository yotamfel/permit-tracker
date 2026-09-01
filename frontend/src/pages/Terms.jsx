const EFFECTIVE_DATE = "September 1, 2026";

export default function Terms() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Terms of Service</h1>
      <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">Effective {EFFECTIVE_DATE}</p>

      <div className="mt-6 space-y-6 text-stone-800 dark:text-stone-300">
        <Section title="1. Acceptance of these terms">
          <p>
            These Terms of Service ("Terms") govern your use of Permit Tracker (the "Service"). By creating an
            account or using the Service, you agree to these Terms and to our{" "}
            <a href="/privacy" target="_blank" rel="noreferrer" className="text-amber-700 underline dark:text-amber-400">
              Privacy Policy
            </a>
            . If you do not agree, do not use the Service.
          </p>
        </Section>

        <Section title="2. What the Service is">
          <p>
            Permit Tracker is an information and preparation tool. We research, organize, and summarize publicly
            available information about official travel permits, quotas, lotteries, and similar access-controlled
            experiences, and provide checklists, reminders, and calendar tools to help you prepare.
          </p>
          <p className="mt-2 font-medium">
            We are not a government agency, park authority, tour operator, or the issuer of any permit. We do not
            process, submit, or guarantee the outcome of any application, registration, or lottery entry on your
            behalf.
          </p>
        </Section>

        <Section title="3. No guarantee of accuracy or outcome">
          <p>
            Permit rules, prices, quotas, dates, and application processes are set by third-party authorities and
            change without notice. We make reasonable efforts to keep information current and note when it was last
            verified, but we do not guarantee that any information on the Service is accurate, complete, or
            up to date at the moment you rely on it. Always confirm critical details (dates, prices, required
            documents) directly with the official issuing authority before making travel decisions.
          </p>
          <p className="mt-2">
            We do not guarantee that you will successfully obtain any permit, win any lottery, or secure any quota
            spot. Competitiveness ratings shown on the Service are general estimates, not predictions for your
            specific application.
          </p>
        </Section>

        <Section title="4. Accounts">
          <p>
            You must provide accurate information when creating an account and are responsible for keeping your
            login credentials secure and for all activity under your account. You must be at least 18 years old to
            create an account.
          </p>
        </Section>

        <Section title="5. Purchases and payment">
          <p>
            Some destinations require a one-time payment to unlock full checklist details, mechanism explanations,
            and related tools. Payments are processed by Stripe; we do not receive or store your full card details.
          </p>
          <p className="mt-2 font-medium">
            Because unlocked content is digital and accessible to you immediately upon payment, purchases are
            non-refundable, except where a refund is required by applicable consumer protection law.
          </p>
        </Section>

        <Section title="6. Alerts and notifications">
          <p>
            You may opt in to email alerts about upcoming application windows. We do our best to send these on
            time, but we do not guarantee delivery, timing, or that an alert will reach you before a window opens.
            You remain responsible for tracking deadlines that matter to you.
          </p>
        </Section>

        <Section title="7. Third-party links and services">
          <p>
            The Service links to official government, park authority, and booking websites, and relies on
            third-party providers (including Google Sign-In, Stripe, and our email and hosting providers) to
            operate. We do not control these third parties, are not responsible for their content, availability, or
            practices, and linking to a site is not an endorsement of it. Your use of any third-party site or
            service is governed by that provider's own terms.
          </p>
        </Section>

        <Section title="8. Acceptable use">
          <p>You agree not to:</p>
          <ul className="mt-2 list-disc space-y-1 ps-5">
            <li>Scrape, systematically copy, or redistribute Service content without our permission</li>
            <li>Attempt to gain unauthorized access to accounts, data, or systems</li>
            <li>Use the Service to impersonate any person or entity</li>
            <li>Interfere with or disrupt the Service or its infrastructure</li>
            <li>Use the Service for any unlawful purpose</li>
          </ul>
        </Section>

        <Section title="9. Intellectual property">
          <p>
            The compiled checklists, summaries, design, and other original content on the Service belong to Permit
            Tracker. Trademarks, names, and content belonging to government agencies, park authorities, and other
            third parties remain the property of their respective owners and are referenced for informational
            purposes only.
          </p>
        </Section>

        <Section title="10. Disclaimer of warranties">
          <p>
            The Service is provided "as is" and "as available," without warranties of any kind, whether express or
            implied, including implied warranties of merchantability, fitness for a particular purpose, and
            non-infringement.
          </p>
        </Section>

        <Section title="11. Limitation of liability">
          <p>
            To the maximum extent permitted by law, Permit Tracker will not be liable for any indirect, incidental,
            or consequential damages (including the cost of a missed trip or booking) arising from your use of the
            Service. Our total liability for any claim relating to a specific destination is limited to the amount
            you paid to unlock that destination, if any.
          </p>
        </Section>

        <Section title="12. Termination">
          <p>
            You may stop using the Service at any time. We may suspend or terminate accounts that violate these
            Terms or that we reasonably believe pose a risk to the Service or other users.
          </p>
        </Section>

        <Section title="13. Changes to these terms">
          <p>
            We may update these Terms from time to time. If we make material changes, we will update the effective
            date above. Continuing to use the Service after changes take effect means you accept the updated Terms.
          </p>
        </Section>

        <Section title="14. Governing law">
          <p>
            These Terms are governed by the laws of the State of Israel, without regard to conflict-of-law
            principles. Any dispute arising from these Terms or the Service will be subject to the exclusive
            jurisdiction of the competent courts of Israel.
          </p>
        </Section>

        <Section title="15. Contact">
          <p>
            Questions about these Terms? Reach us via the{" "}
            <a href="/contact" className="text-amber-700 underline dark:text-amber-400">
              Contact page
            </a>
            .
          </p>
        </Section>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <section>
      <h2 className="text-lg font-semibold text-stone-900 dark:text-stone-100">{title}</h2>
      <div className="mt-2 text-sm leading-relaxed">{children}</div>
    </section>
  );
}
