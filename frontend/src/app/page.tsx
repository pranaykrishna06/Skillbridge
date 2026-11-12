
import Link from "next/link";
import {
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  GraduationCap,
  Search,
  Sparkles,
  Zap,
  BookOpen,
  ClipboardList,
  Bell,
} from "lucide-react";

const features = [
  {
    icon: Search,
    title: "Internship Discovery",
    description:
      "Browse available internship opportunities and search by title, company, or location.",
    color: "bg-violet-100 text-violet-600",
  },
  {
    icon: ClipboardList,
    title: "Application Tracking",
    description:
      "Submit applications and follow their status from one convenient workspace.",
    color: "bg-blue-100 text-blue-600",
  },
  {
    icon: BookOpen,
    title: "Saved Opportunities",
    description:
      "Save interesting internships and return to them whenever you are ready.",
    color: "bg-emerald-100 text-emerald-600",
  },
  {
    icon: BriefcaseBusiness,
    title: "Recruiter Workspace",
    description:
      "Create and manage internship listings for your organization.",
    color: "bg-orange-100 text-orange-600",
  },
  {
    icon: GraduationCap,
    title: "Student Profiles",
    description:
      "Maintain your academic details and present your background to recruiters.",
    color: "bg-pink-100 text-pink-600",
  },
  {
    icon: Bell,
    title: "Application Notifications",
    description:
      "Receive updates when your internship application changes status.",
    color: "bg-cyan-100 text-cyan-600",
  },
];

const steps = [
  {
    number: "01",
    title: "Create your profile",
    description:
      "Add your academic information, projects, experience, and technical skills.",
  },
  {
    number: "02",
    title: "Discover your opportunities",
    description:
      "Browse available internships and choose the opportunities you want to apply for.",
  },
  {
    number: "03",
    title: "Improve your skills",
    description:
      "Submit applications and keep track of their progress.",
  },
  {
    number: "04",
    title: "Become internship-ready",
    description:
      "Track your progress and move closer to your career goals.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* NAVIGATION */}
      <nav className="sticky top-0 z-50 border-b border-gray-100 bg-white/90 backdrop-blur-xl">
        <div className="container-main flex h-[76px] items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-lg shadow-indigo-200">
              <GraduationCap size={24} />
            </div>
            <span className="text-xl font-extrabold tracking-tight text-gray-900">
              Skill<span className="text-indigo-600">Bridge</span>
            </span>
          </Link>

          <div className="hidden items-center gap-9 text-sm font-medium text-gray-600 md:flex">
            <a href="#features" className="hover:text-indigo-600">
              Features
            </a>
            <a href="#how-it-works" className="hover:text-indigo-600">
              How it works
            </a>
            <a href="#about" className="hover:text-indigo-600">
              About
            </a>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="hidden rounded-lg px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-100 sm:block"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-200 transition hover:bg-indigo-700"
            >
              Get Started <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <section className="hero-glow overflow-hidden">
        <div className="container-main grid min-h-[590px] items-center gap-12 py-20 lg:grid-cols-2">
          <div>
            <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700">
              <Sparkles size={16} />
              Your career journey starts here
            </div>

            <h1 className="max-w-2xl text-5xl font-extrabold leading-[1.12] tracking-tight text-gray-950 md:text-6xl">
              Bridge the gap between your{" "}
              <span className="gradient-text">skills</span> and your{" "}
              <span className="gradient-text">dream career.</span>
            </h1>

            <p className="mt-7 max-w-xl text-lg leading-8 text-gray-500">
              Browse internship opportunities, apply for roles, and track your
              application progress in one place.
            </p>

            <div className="mt-9 flex flex-wrap gap-4">
              <Link
                href="/register"
                className="flex items-center gap-2 rounded-xl bg-indigo-600 px-7 py-4 font-semibold text-white shadow-xl shadow-indigo-200 transition hover:-translate-y-1 hover:bg-indigo-700"
              >
                Start Your Journey <ArrowRight size={18} />
              </Link>

              <Link
                href="/login"
                className="rounded-xl border border-gray-200 bg-white px-7 py-4 font-semibold text-gray-700 transition hover:border-indigo-300 hover:text-indigo-600"
              >
                Explore Platform
              </Link>
            </div>

            <div className="mt-9 flex flex-wrap items-center gap-5 text-sm text-gray-500">
              <span className="flex items-center gap-2">
                <CheckCircle2 size={17} className="text-emerald-500" />
                Internship listings
              </span>
              <span className="flex items-center gap-2">
                <CheckCircle2 size={17} className="text-emerald-500" />
                Application tracking
              </span>
            </div>
          </div>

          {/* DASHBOARD PREVIEW */}
          <div className="relative mx-auto w-full max-w-[510px]">
            <div className="absolute -inset-6 rounded-[40px] bg-gradient-to-br from-indigo-200/60 to-purple-100/50 blur-2xl" />

            <div className="relative rounded-3xl border border-gray-200 bg-white p-6 shadow-2xl shadow-indigo-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Your career dashboard</p>
                  <h3 className="mt-1 text-xl font-bold text-gray-900">
                    Welcome back!
                  </h3>
                </div>
                <div className="rounded-xl bg-indigo-50 p-3 text-indigo-600">
                  <Zap size={22} />
                </div>
              </div>

              <div className="mt-7 grid grid-cols-2 gap-4">
                <div className="rounded-2xl bg-indigo-50 p-4">
                  <p className="text-sm text-indigo-600">Applications</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">03</p>
                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-indigo-100">
                    <div className="h-full w-[03] rounded-full bg-indigo-600" />
                  </div>
                </div>

                <div className="rounded-2xl bg-emerald-50 p-4">
                  <p className="text-sm text-emerald-700">Open roles</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">08</p>
                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-emerald-100">
                    <div className="h-full w-[08] rounded-full bg-emerald-500" />
                  </div>
                </div>
              </div>

              <div className="mt-6 rounded-2xl border border-gray-100 p-5">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-gray-900">
                    Recent applications
                  </h4>
                  <Sparkles size={18} className="text-indigo-500" />
                </div>

                {[
                  ["Machine Learning Intern", "Applied", "bg-indigo-500"],
                  ["Cloud Engineering Intern", "Shortlisted", "bg-blue-500"],
                  ["Data Analyst Intern", "Under Review", "bg-emerald-500"],
                ].map(([name, percentage, color]) => (
                  <div key={name} className="mt-5">
                    <div className="mb-2 flex justify-between text-sm">
                      <span className="font-medium text-gray-700">{name}</span>
                      <span className="text-gray-500">{percentage}</span>
                    </div>
                    <div className="h-2 rounded-full bg-gray-100">
                      <div
                        className={`h-full rounded-full ${color}`}
                        style={{ width: percentage }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5 flex items-center gap-3 rounded-xl bg-violet-50 p-4">
                <div className="rounded-lg bg-white p-2 text-violet-600">
                  <ClipboardList size={21} />
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-800">
                    Application update
                  </p>
                  <p className="text-xs text-gray-500">
                    Review the latest status of your applications.
                  </p>
                </div>
              </div>
            </div>

            <div className="absolute -left-8 top-1/3 hidden items-center gap-2 rounded-xl border border-gray-100 bg-white p-3 shadow-xl sm:flex">
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                <CheckCircle2 size={19} />
              </div>
              <span className="text-sm font-semibold text-gray-700">
                Skills improving!
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className="bg-gray-50 py-24">
        <div className="container-main">
          <div className="mx-auto max-w-2xl text-center">
            <span className="text-sm font-bold uppercase tracking-[0.2em] text-indigo-600">
              What we offer
            </span>
            <h2 className="mt-4 text-4xl font-extrabold tracking-tight text-gray-900">
              Everything you need to grow
            </h2>
            <p className="mt-5 leading-7 text-gray-500">
              A unified platform for students to find internships and for recruiters
              to manage listings and applications.
            </p>
          </div>

          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon;

              return (
                <div
                  key={feature.title}
                  className="feature-card rounded-2xl border border-gray-100 bg-white p-7"
                >
                  <div className={`mb-6 inline-flex rounded-xl p-3 ${feature.color}`}>
                    <Icon size={25} />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">
                    {feature.title}
                  </h3>
                  <p className="mt-3 text-sm leading-7 text-gray-500">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="bg-white py-24">
        <div className="container-main">
          <div className="text-center">
            <span className="text-sm font-bold uppercase tracking-[0.2em] text-indigo-600">
              Simple process
            </span>
            <h2 className="mt-4 text-4xl font-extrabold text-gray-900">
              Your journey in four steps
            </h2>
          </div>

          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((step) => (
              <div key={step.number} className="relative">
                <span className="text-5xl font-extrabold text-indigo-100">
                  {step.number}
                </span>
                <h3 className="mt-5 text-lg font-bold text-gray-900">
                  {step.title}
                </h3>
                <p className="mt-3 text-sm leading-7 text-gray-500">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ABOUT / CTA */}
      <section id="about" className="bg-gray-950 py-20">
        <div className="container-main text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-500 text-white">
            <GraduationCap size={30} />
          </div>
          <h2 className="mx-auto mt-7 max-w-2xl text-4xl font-extrabold text-white">
            Your potential deserves the right opportunity.
          </h2>
          <p className="mx-auto mt-5 max-w-xl leading-7 text-gray-400">
            Build your professional future by discovering internships and tracking
            your applications in one place.
          </p>
          <Link
            href="/register"
            className="mt-9 inline-flex items-center gap-2 rounded-xl bg-indigo-500 px-8 py-4 font-semibold text-white transition hover:bg-indigo-400"
          >
            Create Your Account <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-gray-100 bg-white py-8">
        <div className="container-main flex flex-col items-center justify-between gap-4 sm:flex-row">
          <Link href="/" className="text-lg font-extrabold text-gray-900">
            Skill<span className="text-indigo-600">Bridge</span>
          </Link>
          <p className="text-sm text-gray-500">
            Connecting skills with opportunities.
          </p>
          <p className="text-sm text-gray-400">
            © 2026 SkillBridge. All rights reserved.
          </p>
        </div>
      </footer>
    </main>
  );
}
