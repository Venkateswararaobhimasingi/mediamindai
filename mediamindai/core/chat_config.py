USE_CASES = {
    "linkedin": {
        "label": "LinkedIn Post",
        "questions": [
            {
                "key": "topic",
                "question": "What is the post topic?",
                "options": None
            },
            {
                "key": "purpose",
                "question": "Purpose?",
                "options": ["Hiring", "Achievement", "Update"]
            },
            {
                "key": "audience",
                "question": "Target audience?",
                "options": ["All", "Developers", "Founders", "Recruiters"]
            },
            {
                "key": "tone",
                "question": "Tone?",
                "options": ["Professional", "Friendly", "Inspirational"]
            }
        ],
        "role": "professional LinkedIn content writer"
    },

    "email": {
        "label": "Professional Email",
        "questions": [
            {
                "key": "email_type",
                "question": "Email type?",
                "options": ["Job", "Follow-up", "Cold"]
            },
            {
                "key": "recipient_role",
                "question": "Recipient role?",
                "options": None
            },
            {
                "key": "main_message",
                "question": "Main message (short)?",
                "options": None
            },
            {
                "key": "tone",
                "question": "Tone?",
                "options": ["Formal", "Polite", "Friendly"]
            }
        ],
        "role": "professional business email writer"
    },

    "marketing": {
        "label": "Marketing Ad Caption",
        "questions": [
            {
                "key": "platform",
                "question": "Platform?",
                "options": ["Instagram", "Facebook", "Google"]
            },
            {
                "key": "product",
                "question": "Product or Service?",
                "options": None
            },
            {
                "key": "target_audience",
                "question": "Target audience?",
                "options": None
            },
            {
                "key": "cta",
                "question": "Call To Action?",
                "options": ["Buy Now", "Sign Up", "Learn More"]
            }
        ],
        "role": "digital marketing copywriter"
    },

    "instagram": {
        "label": "Instagram Post",
        "questions": [
            {
                "key": "topic",
                "question": "Post topic?",
                "options": None
            },
            {
                "key": "goal",
                "question": "Post goal?",
                "options": ["Engagement", "Promotion"]
            },
            {
                "key": "tone",
                "question": "Tone?",
                "options": ["Fun", "Bold", "Informative"]
            },
            {
                "key": "trend",
                "question": "Trend-based?",
                "options": ["Yes", "No"]
            }
        ],
        "role": "social media content creator"
    },

    "resume": {
        "label": "Resume Summary",
        "questions": [
            {
                "key": "role",
                "question": "Target role?",
                "options": None
            },
            {
                "key": "experience",
                "question": "Experience level?",
                "options": ["Fresher", "1–3 Years", "3–5 Years", "5+ Years"]
            },
            {
                "key": "skills",
                "question": "Key skills (comma-separated)?",
                "options": None
            },
            {
                "key": "goal",
                "question": "Career goal?",
                "options": None
            }
        ],
        "role": "professional resume summary writer"
    },

    "review": {
        "label": "Product Review",
        "questions": [
            {
                "key": "product",
                "question": "Product name?",
                "options": None
            },
            {
                "key": "experience",
                "question": "Experience?",
                "options": ["Positive", "Neutral", "Negative"]
            },
            {
                "key": "platform",
                "question": "Review platform?",
                "options": ["Amazon", "Flipkart", "Google"]
            },
            {
                "key": "points",
                "question": "Key points to mention?",
                "options": None
            }
        ],
        "role": "genuine customer writing a real review"
    }
}
