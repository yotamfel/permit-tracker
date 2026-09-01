const EFFECTIVE_DATE = "September 1, 2026";

export default function Privacy() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold text-stone-900 dark:text-stone-100">Privacy Policy</h1>
      <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">Effective {EFFECTIVE_DATE}</p>

      <div className="mt-6 space-y-6 text-stone-800 dark:text-stone-300">
        <Section title="1. Overview">
          <p>
            This Privacy Policy explains what information Permit Tracker ("we," "us") collects when you use our
            website, how we use it, and the choices you have. By using the Service you agree to this Policy and to
            our{" "}
            <a href="/terms" target="_blank" rel="noreferrer" className="text-amber-700 underline dark:text-amber-400">
              Terms of Service
            </a>
            .
          </p>
        </Section>

        <Section title="2. Information we collect">
          <ul className="list-disc space-y-1.5 ps-5">
            <li>
              <span className="font-medium">Account information:</span> the email address and password you provide
              (we store a one-way hash of your password, never the password itself), or your name and email if you
              sign in with Google.
            </li>
            <li>
              <span className="font-medium">Preferences:</span> your language and light/dark theme preference.
            </li>
            <li>
              <span className="font-medium">Purchases:</span> which destinations you've unlocked. Payments are
              handled entirely by Stripe - we never receive or store your full card number.
            </li>
            <li>
              <span className="font-medium">Alerts:</span> the destinations you've set alerts for and your chosen
              lead time or travel date.
            </li>
            <li>
              <span className="font-medium">Checklist progress:</span> which checklist items you've marked done for
              destinations you've unlocked.
            </li>
            <li>
              <span className="font-medium">Contact messages:</span> the name, email, and message you submit
              through our Contact page.
            </li>
            <li>
              <span className="font-medium">Technical data:</span> standard server logs (such as IP address,
              browser type, and request timestamps) automatically collected by our hosting providers as part of
              normal operation.
            </li>
          </ul>
        </Section>

        <Section title="3. How we use this information">
          <p>We use the information above to:</p>
          <ul className="mt-2 list-disc space-y-1 ps-5">
            <li>Create and maintain your account, and let you log in</li>
            <li>Process payments for destinations you unlock</li>
            <li>Send the alert emails you've opted into, and reply to messages you send us</li>
            <li>Show you your unlocked destinations and checklist progress</li>
            <li>Maintain and improve the Service, and prevent abuse</li>
          </ul>
        </Section>

        <Section title="4. Who we share information with">
          <p>We do not sell your personal data. We share information only with the service providers we rely on to operate Permit Tracker:</p>
          <ul className="mt-2 list-disc space-y-1 ps-5">
            <li>
              <span className="font-medium">Stripe</span> - to process payments (they receive your payment details
              directly; we don't).
            </li>
            <li>
              <span className="font-medium">Google</span> - only if you choose to sign in with Google.
            </li>
            <li>
              <span className="font-medium">Our email provider</span> - to send account and alert emails.
            </li>
            <li>
              <span className="font-medium">Our hosting and database providers</span> - to run the website, backend,
              and store data securely.
            </li>
          </ul>
          <p className="mt-2">We may also disclose information if required to by law.</p>
        </Section>

        <Section title="5. Cookies and local storage">
          <p>
            We use your browser's local storage (not tracking cookies) to keep you logged in and to remember your
            theme preference. We do not use third-party advertising or tracking scripts.
          </p>
        </Section>

        <Section title="6. Data retention">
          <p>
            We keep your account information for as long as your account is active. If you'd like your account and
            associated data deleted, contact us (see below) and we will process your request.
          </p>
        </Section>

        <Section title="7. Your rights">
          <p>
            You can ask us to access, correct, or delete your personal data, or unsubscribe from alert emails at any
            time, by reaching us through the{" "}
            <a href="/contact" className="text-amber-700 underline dark:text-amber-400">
              Contact page
            </a>
            .
          </p>
        </Section>

        <Section title="8. Children's privacy">
          <p>
            The Service is not directed at, and we do not knowingly collect personal data from, anyone under 18.
          </p>
        </Section>

        <Section title="9. Security">
          <p>
            We take reasonable technical measures to protect your data, including hashing passwords and encrypting
            connections to our servers. No method of transmission or storage is completely secure, and we cannot
            guarantee absolute security.
          </p>
        </Section>

        <Section title="10. International data transfer">
          <p>
            Our hosting and infrastructure providers may process and store data outside of your home country,
            including in the United States and the European Union. By using the Service, you consent to this
            transfer.
          </p>
        </Section>

        <Section title="11. Changes to this policy">
          <p>
            We may update this Privacy Policy from time to time. If we make material changes, we will update the
            effective date above.
          </p>
        </Section>

        <Section title="12. Contact">
          <p>
            Questions about this Policy or your data? Reach us via the{" "}
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
