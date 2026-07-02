import { branding } from "@/config/branding";

export const authInfoPages = [
  {
    slug: "election-period",
    routeName: "auth-info-election-period",
    title: "Election period",
    summary: "When voting is open and what to expect.",
    icon: "elections",
  },
  {
    slug: "voting-instructions",
    routeName: "auth-info-voting-instructions",
    title: "Voting instructions",
    summary: "How to sign in and cast your ballot.",
    icon: "profile",
  },
  {
    slug: "security",
    routeName: "auth-info-security",
    title: "Security information",
    summary: "How your vote and identity are protected.",
    icon: "security",
  },
  {
    slug: "help",
    routeName: "auth-info-help",
    title: "Help & FAQ",
    summary: "Common questions and support contacts.",
    icon: "inbox",
  },
];

export function getAuthInfoContent(slug) {
  const institution = branding.institutionName;
  const email = branding.electionOfficeEmail;
  const phone = branding.electionOfficePhone;

  const content = {
    "election-period": {
      title: "Election period",
      intro:
        "Campus elections run for a fixed period set by the election office. Voting is only available while an election is open.",
      sections: [
        {
          heading: "When you can vote",
          body: "Sign in during the published voting window for SRC, faculty, or departmental elections. The portal will show open ballots only when voting is active.",
        },
        {
          heading: "Before voting opens",
          body: "Confirm you can sign in with your index number. Contact the election office if you cannot access the portal before election day.",
        },
        {
          heading: "After voting closes",
          body: "Ballots can no longer be changed once an election closes. Certified results are published through official channels at " +
            institution +
            ".",
        },
      ],
    },
    "voting-instructions": {
      title: "Voting instructions",
      intro: "Follow these steps to cast your ballot securely.",
      sections: [
        {
          heading: "1. Sign in",
          body: "Enter your index number, then continue. You will receive a one-time code on your registered phone or email.",
        },
        {
          heading: "2. Verify your identity",
          body: "Enter the one-time code sent to your registered phone or email.",
        },
        {
          heading: "3. Select candidates",
          body: "Open each position on your ballot, choose one candidate per position, and review your selections.",
        },
        {
          heading: "4. Submit your ballot",
          body: "Confirm and submit once. Each eligible student may vote once per election.",
        },
      ],
    },
    security: {
      title: "Security information",
      intro: "VoteBridge is designed to protect ballot secrecy and election integrity.",
      sections: [
        {
          heading: "Identity verification",
          body: "You must sign in with your index number and a one-time verification code before accessing a ballot.",
        },
        {
          heading: "Ballot protection",
          body: "Your vote is recorded once per election. Ballot data is encrypted in transit and stored for audit and certification.",
        },
        {
          heading: "While voting is open",
          body: "Live rankings, vote totals, and winners are not shown to protect the integrity of the process.",
        },
        {
          heading: "Report concerns",
          body: `Contact the election office immediately if you notice suspicious activity: ${email}.`,
        },
      ],
    },
    help: {
      title: "Help & FAQ",
      intro: "Quick answers for students using the elections portal.",
      sections: [
        {
          heading: "I cannot sign in",
          body: "Check your index number format (e.g. BC/ITS/24/047). If the problem continues, contact the election office.",
        },
        {
          heading: "I did not receive an OTP code",
          body: "Wait a minute, then use Resend code on the verification screen. Ensure your contact details are up to date with the institution.",
        },
        {
          heading: "Can I change my vote?",
          body: "No. Once submitted, a ballot cannot be changed. Review your choices carefully before confirming.",
        },
        {
          heading: "Who can I contact?",
          body: `Election office: ${email}${phone ? ` · ${phone}` : ""}.`,
        },
      ],
    },
  };

  return content[slug] || null;
}
