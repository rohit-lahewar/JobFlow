"""
Seed Script for JobFlow — Development & Demo Data
Creates sample user account and realistic job applications, interview rounds, follow-ups, and notes.

Demo Account Credentials:
  Email:    demo@jobflow.dev
  Password: Demo1234!
"""
import os
from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models import User, Application, Interview, FollowUp, Note

app = create_app(os.environ.get('FLASK_CONFIG', 'development'))


def seed_database():
    with app.app_context():
        print("=" * 60)
        print(" JobFlow — Seeding Development / Demo Data")
        print("=" * 60)
        db.create_all()

        # 1. Create or retrieve demo user
        demo_email = "demo@jobflow.dev"
        user = User.query.filter_by(email=demo_email).first()

        if user:
            print(f"[!] Existing demo user found ({demo_email}). Cleaning up previous demo data...")
            # Clean up user's existing records
            Application.query.filter_by(user_id=user.id).delete()
            db.session.commit()
        else:
            print(f"[+] Creating demo user: {demo_email}")
            user = User(
                name="Alex Johnson",
                email=demo_email
            )
            user.set_password("Demo1234!")
            db.session.add(user)
            db.session.commit()

        print(f"  [OK] User ready (ID: {user.id})")

        today = date.today()

        # 2. Sample Applications
        applications_data = [
            {
                'company_name': 'Stripe',
                'job_title': 'Senior Backend Engineer (Python / API)',
                'location': 'San Francisco, CA / Remote',
                'employment_type': 'Full Time',
                'work_mode': 'Remote',
                'salary': '$165,000 - $185,000',
                'job_url': 'https://stripe.com/jobs/backend-engineer',
                'application_date': today - timedelta(days=22),
                'status': 'Offer',
                'priority': 'High',
                'recruiter_name': 'Emily Watson',
                'recruiter_email': 'emily.watson@stripe.com',
                'job_description': 'Build resilient financial infrastructure using Python, distributed systems, and modern REST APIs.',
                'notes': 'Referred by tech lead. Completed all rounds with high ratings in API architecture.'
            },
            {
                'company_name': 'Google',
                'job_title': 'Software Engineer III — Cloud Platform',
                'location': 'Mountain View, CA',
                'employment_type': 'Full Time',
                'work_mode': 'Hybrid',
                'salary': '$175,000 - $195,000',
                'job_url': 'https://careers.google.com/jobs/swe-cloud',
                'application_date': today - timedelta(days=15),
                'status': 'Interview',
                'priority': 'High',
                'recruiter_name': 'Marcus Vance',
                'recruiter_email': 'mvance@google.com',
                'job_description': 'Design scalable cloud microservices, develop automated pipelines, and enhance Kubernetes integrations.',
                'notes': 'Passed recruiter screen and phone technical. Preparing for virtual onsite system design.'
            },
            {
                'company_name': 'Datadog',
                'job_title': 'Python Systems Engineer',
                'location': 'New York, NY',
                'employment_type': 'Full Time',
                'work_mode': 'Hybrid',
                'salary': '$150,000 - $170,000',
                'job_url': 'https://careers.datadoghq.com/job/python-engineer',
                'application_date': today - timedelta(days=10),
                'status': 'Interview',
                'priority': 'Medium',
                'recruiter_name': 'Jessica Miller',
                'recruiter_email': 'jmiller@datadoghq.com',
                'job_description': 'High-performance observability agents, metric aggregation, and time-series telemetry.',
                'notes': 'Technical take-home test submitted. Interview scheduled for next week.'
            },
            {
                'company_name': 'Netflix',
                'job_title': 'Platform Engineer — Streaming Core',
                'location': 'Los Gatos, CA / Remote',
                'employment_type': 'Full Time',
                'work_mode': 'Remote',
                'salary': '$210,000',
                'job_url': 'https://jobs.netflix.com/jobs/streaming-core',
                'application_date': today - timedelta(days=30),
                'status': 'Shortlisted',
                'priority': 'High',
                'recruiter_name': 'Carlos Mendez',
                'recruiter_email': 'cmendez@netflix.com',
                'job_description': 'Distributed edge caching services and high-concurrency streaming optimization.',
                'notes': 'Resume reviewed by hiring manager. Awaiting initial screening invite.'
            },
            {
                'company_name': 'Amazon Web Services',
                'job_title': 'Software Development Engineer II',
                'location': 'Seattle, WA',
                'employment_type': 'Full Time',
                'work_mode': 'On-site',
                'salary': '$155,000',
                'job_url': 'https://amazon.jobs/aws-sde2',
                'application_date': today - timedelta(days=45),
                'status': 'Rejected',
                'priority': 'Medium',
                'recruiter_name': 'Priya Patel',
                'recruiter_email': 'ppatel@amazon.com',
                'job_description': 'Internal developer tooling, distributed queuing, and automated provisioning.',
                'notes': 'Made it through 2 rounds. Decision went to an internal candidate. Reapply in 6 months.'
            },
            {
                'company_name': 'Cloudflare',
                'job_title': 'Full-Stack Python / JavaScript Engineer',
                'location': 'Austin, TX / Remote',
                'employment_type': 'Full Time',
                'work_mode': 'Remote',
                'salary': '$145,000 - $160,000',
                'job_url': 'https://cloudflare.com/careers/fs-python',
                'application_date': today - timedelta(days=5),
                'status': 'Applied',
                'priority': 'Medium',
                'recruiter_name': None,
                'recruiter_email': None,
                'job_description': 'User-facing dashboard interfaces, analytics visualizations, and secure backend APIs.',
                'notes': 'Submitted direct application via company website.'
            },
            {
                'company_name': 'OpenAI',
                'job_title': 'Infrastructure & Tooling Engineer',
                'location': 'San Francisco, CA',
                'employment_type': 'Full Time',
                'work_mode': 'Hybrid',
                'salary': '$190,000 - $220,000',
                'job_url': 'https://openai.com/careers/infra',
                'application_date': today - timedelta(days=3),
                'status': 'Applied',
                'priority': 'High',
                'recruiter_name': 'David Ross',
                'recruiter_email': 'dross@openai.com',
                'job_description': 'Compute cluster orchestration, developer environment tooling, and model deployment pipelines.',
                'notes': 'Referred by senior researcher.'
            }
        ]

        created_apps = []
        for app_data in applications_data:
            app_record = Application(user_id=user.id, **app_data)
            db.session.add(app_record)
            created_apps.append(app_record)

        db.session.commit()
        print(f"[+] Created {len(created_apps)} sample job applications.")

        # 3. Create Sample Interviews
        stripe_app = next(a for a in created_apps if a.company_name == 'Stripe')
        google_app = next(a for a in created_apps if a.company_name == 'Google')
        datadog_app = next(a for a in created_apps if a.company_name == 'Datadog')

        interviews_data = [
            # Stripe completed rounds
            {
                'application_id': stripe_app.id,
                'round_name': 'Technical Round 1',
                'interview_type': 'Online',
                'interview_date': today - timedelta(days=18),
                'start_time': '10:00 AM PST',
                'interviewer': 'Sarah Chen (Staff SWE)',
                'meeting_link': 'https://meet.google.com/stripe-tech-1',
                'status': 'Passed',
                'notes': 'Live coding: Data structures, rate-limiting algorithms, and concurrency in Python.'
            },
            {
                'application_id': stripe_app.id,
                'round_name': 'Technical Round 2',
                'interview_type': 'Online',
                'interview_date': today - timedelta(days=12),
                'start_time': '2:00 PM PST',
                'interviewer': 'Liam Miller (Principal Architect)',
                'meeting_link': 'https://meet.google.com/stripe-arch-2',
                'status': 'Passed',
                'notes': 'System Design: Designing an idempotent payment webhook event delivery system.'
            },
            {
                'application_id': stripe_app.id,
                'round_name': 'Final Round',
                'interview_type': 'Online',
                'interview_date': today - timedelta(days=5),
                'start_time': '1:00 PM PST',
                'interviewer': 'Director of Engineering',
                'meeting_link': 'https://meet.google.com/stripe-final',
                'status': 'Completed',
                'notes': 'Culture, leadership principles, engineering management alignment.'
            },
            # Google upcoming and past rounds
            {
                'application_id': google_app.id,
                'round_name': 'Online Assessment',
                'interview_type': 'Online',
                'interview_date': today - timedelta(days=8),
                'start_time': '11:00 AM PST',
                'interviewer': 'Automated HackerRank Assessment',
                'meeting_link': 'https://hackerrank.com/test/google-swe',
                'status': 'Passed',
                'notes': 'Score: 100%. Graph traversal and dynamic programming problems.'
            },
            {
                'application_id': google_app.id,
                'round_name': 'Technical Round 1',
                'interview_type': 'Online',
                'interview_date': today + timedelta(days=3),
                'start_time': '1:30 PM PST',
                'interviewer': 'Google Cloud SWE Team',
                'meeting_link': 'https://meet.google.com/cloud-swe-r1',
                'status': 'Scheduled',
                'notes': 'Brush up on distributed caching and LRU cache implementations in Python.'
            },
            # Datadog upcoming round
            {
                'application_id': datadog_app.id,
                'round_name': 'Technical Round 1',
                'interview_type': 'Online',
                'interview_date': today + timedelta(days=6),
                'start_time': '3:00 PM EST',
                'interviewer': 'Alex Rivera (Agent Team Lead)',
                'meeting_link': 'https://zoom.us/j/datadog-round-1',
                'status': 'Scheduled',
                'notes': 'Deep dive into Python GIL, multiprocessing, and socket communication.'
            }
        ]

        for iv_data in interviews_data:
            iv_record = Interview(**iv_data)
            db.session.add(iv_record)

        # 4. Create Sample Follow-ups
        followups_data = [
            {
                'application_id': google_app.id,
                'followup_date': today + timedelta(days=1),
                'followup_type': 'Email',
                'status': 'Pending',
                'notes': 'Confirm meeting link and audio setup with recruiter Marcus Vance.'
            },
            {
                'application_id': datadog_app.id,
                'followup_date': today + timedelta(days=4),
                'followup_type': 'Email',
                'status': 'Pending',
                'notes': 'Send updated portfolio github repository link to recruiter Jessica.'
            },
            {
                'application_id': stripe_app.id,
                'followup_date': today - timedelta(days=4),
                'followup_type': 'Email',
                'status': 'Completed',
                'notes': 'Sent thank-you note to hiring manager following final round.'
            }
        ]

        for fu_data in followups_data:
            fu_record = FollowUp(**fu_data)
            db.session.add(fu_record)

        # 5. Create Sample Notes
        notes_data = [
            {
                'application_id': stripe_app.id,
                'user_id': user.id,
                'content': 'Offer negotiation notes: Base salary offered is $170k with $40k equity over 4 years. Counter-offering for $180k based on market data.'
            },
            {
                'application_id': google_app.id,
                'user_id': user.id,
                'content': 'Review topics for Round 1: Consistent hashing, CAP theorem trade-offs, and Python generators vs list comprehensions memory footprints.'
            }
        ]

        for n_data in notes_data:
            note_record = Note(**n_data)
            db.session.add(note_record)

        db.session.commit()
        print(f"[+] Created {len(interviews_data)} interview rounds.")
        print(f"[+] Created {len(followups_data)} follow-up reminders.")
        print(f"[+] Created {len(notes_data)} application prep notes.")
        print("-" * 60)
        print(" SUCCESS: Demo seed data generation completed!")
        print(" Login credentials:")
        print(f"   Email:    {demo_email}")
        print("   Password: Demo1234!")
        print("=" * 60)


if __name__ == '__main__':
    seed_database()
