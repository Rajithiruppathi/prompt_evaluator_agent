"""
Platform profiles — format rules, structural expectations, and failure conditions for each use case.

Each profile is self-contained: the system reads these rules at runtime and applies them
without any hardcoded platform logic in the agents themselves.

Adding a new platform: copy any profile block, update all fields, add aliases.
"""

PROFILES: dict[str, dict] = {

    "linkedin_post": {
        "id": "linkedin_post",
        "label": "LinkedIn Post",
        "aliases": ["linkedin", "linkedin post", "linkedin article"],
        "format": {
            "max_chars":    3000,
            "optimal_chars": 1200,
            "max_words":    500,
            "optimal_words": 200,
            "paragraph_style": "Short paragraphs of 2-3 sentences, separated by blank lines",
            "hashtags": {"required": True,  "min": 3, "max": 5, "position": "end"},
            "emojis":   "Optional, max 2, only if they add meaning",
            "sections": ["hook", "insight_or_story", "lesson_or_takeaway", "cta"],
        },
        "hook_rules": {
            "what_works": [
                "A specific, surprising claim that provokes agreement or debate",
                "A personal failure with an honest, specific lesson",
                "A counterintuitive observation about your industry",
                "A specific number that challenges a common assumption",
            ],
            "what_fails": [
                "Starting with 'I am excited to announce'",
                "Starting with your job title or company name",
                "Starting with 'In today's fast-paced world'",
                "A generic motivational opener with no specific claim",
            ],
            "max_chars": 160,
            "note": "First 2 lines appear before 'see more' — they must earn the click",
        },
        "cta_rules": {
            "strong": [
                "Ask a specific, relevant question your audience has a real opinion on",
                "Invite them to share their version of the experience",
                "Ask them to challenge your take with their own data",
            ],
            "weak": [
                "What do you think?",
                "Share if you agree",
                "Let me know your thoughts",
                "Follow for more content",
                "Like if this resonated",
            ],
            "format": "One question or one clear action. Never multiple asks.",
        },
        "structural_requirements": {
            "hook":     "First 1-2 lines visible before 'see more' must earn the read",
            "body":     "Each paragraph max 3 lines — white space is not wasted space",
            "hashtags": "3-5 relevant hashtags at the very end, nowhere else",
        },
        "tone_range": ["Professional", "Conversational", "Direct", "Inspirational"],
        "native_behaviors": [
            "Personal experience outperforms generic advice consistently",
            "Vulnerability drives engagement more than authority signals",
            "Native documents and polls outperform external links",
            "Dwell time matters — write content that makes people stop",
        ],
        "failure_conditions": [
            "Reads like a press release or company blog post",
            "Paragraphs longer than 4 lines — wall-of-text kills reach",
            "More than 5 hashtags — signals spam to both algorithm and reader",
            "Ends with 'Like and share if you found this helpful'",
            "Generic opener that loses attention before 'see more'",
            "Talks about the company instead of the person's experience",
        ],
        "validation": {
            "hashtag_count":    {"min": 3, "max": 5},
            "max_para_words":   50,
            "requires_cta":     True,
            "max_words":        500,
        },
    },

    "blog": {
        "id": "blog",
        "label": "Blog Post",
        "aliases": ["blog", "blog post", "article", "long form", "long-form"],
        "format": {
            "max_words":     2000,
            "optimal_words": 1200,
            "paragraph_style": "4-6 sentences per paragraph with clear topic sentences",
            "hashtags": {"required": False, "min": 0, "max": 0},
            "headings":  "H2 sections with specific, keyword-aware headings; H3 for sub-points",
            "sections":  ["title", "intro", "h2_sections", "conclusion"],
        },
        "hook_rules": {
            "what_works": [
                "A specific, surprising claim in the first paragraph",
                "A story that drops the reader into the middle of a scene",
                "A question the reader is already asking but can't answer",
                "Directly addressing the frustration that brought them here",
            ],
            "what_fails": [
                "Starting with definitions ('What is X?')",
                "Opening with the history of the topic before the value",
                "Starting with 'In today's world'",
                "A paragraph about why the topic matters before getting to it",
            ],
            "max_words": 150,
            "note": "First 150 words determine if they stay — establish the problem and promise immediately",
        },
        "cta_rules": {
            "strong": [
                "Direct to related content they'll want next",
                "Ask a specific question that continues the conversation",
                "Offer a resource that extends the topic meaningfully",
            ],
            "weak": [
                "Subscribe to our newsletter",
                "Let us know what you think in the comments",
                "Share this post if you found it helpful",
            ],
            "format": "Natural conclusion that transitions to the reader's next action",
        },
        "structural_requirements": {
            "title":       "Clear, specific, under 70 characters",
            "intro":       "First 150 words establish the problem and the promise",
            "body":        "H2 sections with specific, descriptive headings",
            "conclusion":  "Land on one key insight — don't summarize everything",
        },
        "tone_range": ["Professional", "Conversational", "Educational", "Analytical"],
        "native_behaviors": [
            "Headers help scanners decide whether to read",
            "First 150 words determine whether they stay or bounce",
            "Practical content outperforms theoretical — show, don't tell",
            "Specific beats general every single time",
        ],
        "failure_conditions": [
            "Wall of text with no headers or visual breathing room",
            "Generic intro that could apply to any blog post on any site",
            "Conclusion that restates all points instead of landing on one insight",
            "Missing a clear, specific point of view",
            "Headings that are labels ('Introduction') instead of specific promises",
        ],
        "validation": {
            "requires_title":  True,
            "max_para_words":  150,
            "requires_cta":    False,
            "max_words":       2000,
        },
    },

    "cold_email": {
        "id": "cold_email",
        "label": "Cold Email",
        "aliases": ["cold email", "outreach email", "sales email", "email outreach", "prospecting email"],
        "format": {
            "max_words":     200,
            "optimal_words": 120,
            "paragraph_style": "2-3 sentences per paragraph, 3 paragraphs maximum",
            "hashtags": {"required": False, "min": 0, "max": 0},
            "sections": ["personalized_opener", "value_proposition", "specific_cta"],
        },
        "hook_rules": {
            "what_works": [
                "Reference something specific about their company, role, or recent work",
                "Lead with a problem they definitely have — stated from their perspective",
                "A specific result achieved for someone in a similar situation",
                "A question that reveals you genuinely understand their world",
            ],
            "what_fails": [
                "Starting with your company name or product name",
                "Starting with 'I hope this email finds you well'",
                "Starting with a generic compliment about their company",
                "A long introduction about yourself before they care who you are",
            ],
            "max_words": 30,
            "note": "Subject line + first sentence = only things they might read. Make them count.",
        },
        "cta_rules": {
            "strong": [
                "Ask for one specific, low-friction action (15-min call, a yes/no reply)",
                "Offer a specific time slot to reduce decision friction",
                "Ask one clear yes/no question",
            ],
            "weak": [
                "Let me know if you'd like to learn more",
                "Feel free to reach out anytime",
                "Looking forward to hearing from you",
                "Please let me know if you're interested",
            ],
            "format": "One ask only. Multiple options create decision paralysis.",
        },
        "structural_requirements": {
            "opener":     "Personalized to them specifically — not just their industry",
            "body":       "One clear value proposition — not a feature list",
            "cta":        "One specific ask with the minimum possible friction",
        },
        "tone_range": ["Direct", "Conversational", "Professional"],
        "native_behaviors": [
            "Shorter than you think is necessary — ruthlessly cut",
            "The ask must be easy to say yes to",
            "No attachments in first touch",
            "Subject line is the hook — be specific, not clever",
        ],
        "failure_conditions": [
            "More than 200 words — no one finishes a long cold email",
            "Talks about you more than them",
            "Multiple asks in the CTA — pick one",
            "Generic opener that could go to any person in any company",
            "No clear value proposition — what's in it for them?",
            "Formal or robotic tone that sounds like a form letter",
        ],
        "validation": {
            "hashtag_count":  {"min": 0, "max": 0},
            "max_para_words": 80,
            "requires_cta":   True,
            "max_words":      200,
        },
    },

    "ad_copy": {
        "id": "ad_copy",
        "label": "Ad Copy",
        "aliases": ["ad copy", "advertisement", "paid ad", "facebook ad", "google ad", "display ad"],
        "format": {
            "max_words":     150,
            "optimal_words": 80,
            "paragraph_style": "Short punchy lines, 1-2 sentences",
            "hashtags": {"required": False, "min": 0, "max": 0},
            "sections": ["headline", "body", "cta"],
        },
        "hook_rules": {
            "what_works": [
                "Lead with the specific problem you solve, not who you are",
                "A number that creates immediate credibility",
                "A question that hits the pain point directly",
                "A bold claim that earns the stop",
            ],
            "what_fails": [
                "Company name before the benefit",
                "Vague benefit statements ('improve your business')",
                "Starting with 'Introducing...'",
                "Clever wordplay that obscures the offer",
            ],
            "max_words": 10,
            "note": "People scroll past ads — interrupt the pattern with specificity",
        },
        "cta_rules": {
            "strong": ["Start Free Trial", "Book a Demo", "Get [Specific Result]", "See How It Works"],
            "weak":   ["Click Here", "Learn More", "Visit Our Website", "Contact Us"],
            "format": "Imperative verb + specific outcome. Not a statement — an action.",
        },
        "structural_requirements": {
            "headline": "Benefit-first, under 10 words",
            "body":     "Expand the benefit with one specific supporting proof",
            "cta":      "Clear imperative, minimum friction",
        },
        "tone_range": ["Direct", "Persuasive", "Casual", "Professional"],
        "native_behaviors": [
            "Specificity converts better than vague benefits",
            "Social proof accelerates decisions",
            "One message per ad — multiple benefits dilute all of them",
            "People decide in 3 seconds — front-load everything",
        ],
        "failure_conditions": [
            "Feature-focused instead of benefit-focused",
            "Weak CTA that doesn't name the action",
            "Multiple competing messages",
            "More than 150 words",
            "Starting with the company or product name",
        ],
        "validation": {
            "requires_cta": True,
            "max_words":    150,
        },
    },

    "twitter_thread": {
        "id": "twitter_thread",
        "label": "Twitter / X Thread",
        "aliases": ["twitter", "tweet", "x thread", "thread", "twitter thread", "x post"],
        "format": {
            "max_words_per_tweet":     280,
            "optimal_words_per_tweet": 200,
            "thread_length":           "5-12 tweets",
            "hashtags": {"required": False, "min": 0, "max": 2},
            "sections": ["hook_tweet", "numbered_body_tweets", "conclusion_tweet"],
            "numbering": "Format: '1/' '2/' '3/' for clarity",
        },
        "hook_rules": {
            "what_works": [
                "A bold claim that makes them want to read the thread",
                "A promise of specific, stealable value",
                "A surprising data point with immediate context",
                "A question with a non-obvious, specific answer",
            ],
            "what_fails": [
                "Starting with 'A thread:' or '🧵'",
                "Starting with 'So I was thinking...'",
                "A generic quote from someone famous",
                "A hook that doesn't work as a standalone tweet",
            ],
            "max_words": 50,
            "note": "Hook tweet determines thread reach — it must work standalone",
        },
        "cta_rules": {
            "strong": [
                "Ask them to add their own point to the thread",
                "Tell them to share the tweet that helped most",
                "Invite them to follow for more on this specific topic",
            ],
            "weak": [
                "Like and RT if helpful",
                "Follow me for more content",
                "Drop a comment below",
            ],
            "format": "Last tweet wraps the key insight + one specific ask",
        },
        "structural_requirements": {
            "hook_tweet":  "Must standalone — most people only see this",
            "body_tweets": "Each tweet complete — no cliffhangers mid-thought",
            "numbering":   "Number every tweet: 1/, 2/, 3/",
        },
        "tone_range": ["Direct", "Conversational", "Educational", "Founder Voice"],
        "native_behaviors": [
            "Most readers only read 3-4 tweets — front-load the value",
            "Short tweets outperform long ones inside threads",
            "Lists and numbered takeaways perform consistently",
            "Hook tweet reach determines thread reach",
        ],
        "failure_conditions": [
            "Hook tweet that doesn't work as a standalone",
            "Tweets that only make sense in sequence",
            "Thread too long — attention dies at tweet 8",
            "No clear payoff in the hook tweet",
        ],
        "validation": {
            "requires_cta": True,
        },
    },

    "seo_article": {
        "id": "seo_article",
        "label": "SEO Article",
        "aliases": ["seo article", "seo content", "seo blog", "search optimized", "seo post"],
        "format": {
            "max_words":     3000,
            "optimal_words": 1800,
            "paragraph_style": "3-5 sentences, clear structure, scannable",
            "hashtags": {"required": False, "min": 0, "max": 0},
            "headings":  "Primary keyword in H1, related terms in H2/H3",
            "sections":  ["title", "intro", "h2_body_sections", "faq", "conclusion"],
        },
        "hook_rules": {
            "what_works": [
                "Address the search intent immediately in the first paragraph",
                "Promise to answer the specific question they searched",
                "Lead with the answer, then explain the reasoning",
            ],
            "what_fails": [
                "Opening with background they didn't search for",
                "Starting without addressing why they landed here",
                "A hook written for social, not for search intent",
            ],
            "max_words": 150,
            "note": "First 150 words must match the intent of the search query",
        },
        "cta_rules": {
            "strong": [
                "Related content that answers their next logical question",
                "A tool or resource that extends the value of the article",
                "A specific next step in their journey on this topic",
            ],
            "weak": [
                "Generic newsletter subscribe",
                "Contact us",
                "Share this post if helpful",
            ],
            "format": "Natural transition to the next action in their search journey",
        },
        "structural_requirements": {
            "title":   "Include primary keyword, under 60 characters for SEO",
            "intro":   "First 150 words address search intent directly",
            "headings": "H2s answer specific sub-questions related to the main query",
            "faq":     "Address secondary keywords and common questions in FAQ format",
        },
        "tone_range": ["Professional", "Educational", "Conversational", "Analytical"],
        "native_behaviors": [
            "Search intent trumps creativity — match what they came for",
            "E-E-A-T signals matter: demonstrate real experience and expertise",
            "Internal links extend session depth and topical authority",
            "Headers and structure help both scanners and crawlers",
        ],
        "failure_conditions": [
            "Title doesn't match the actual search intent",
            "Generic intro that delays the answer they searched for",
            "Missing headings and visual structure",
            "Content anyone could write — no first-hand expertise or experience",
        ],
        "validation": {
            "requires_title": True,
            "max_para_words": 100,
            "requires_cta":   False,
            "max_words":      3000,
        },
    },

    "technical_post": {
        "id": "technical_post",
        "label": "Technical Post",
        "aliases": [
            "technical post", "technical article", "engineering blog",
            "dev post", "technical blog", "engineering post",
        ],
        "format": {
            "max_words":     2500,
            "optimal_words": 1500,
            "code_blocks":   "Required for all code examples",
            "hashtags": {"required": False, "min": 0, "max": 0},
            "sections": ["problem_statement", "approach", "implementation", "results", "lessons"],
        },
        "hook_rules": {
            "what_works": [
                "State the specific problem upfront — what broke or what was insufficient",
                "Show the before state before explaining the after",
                "Lead with an unexpected finding from production",
            ],
            "what_fails": [
                "Starting with the solution before explaining the problem",
                "Generic intro that doesn't establish why this matters to practitioners",
            ],
            "max_words": 100,
        },
        "cta_rules": {
            "strong": [
                "Point to the code, repo, or implementation",
                "Ask a specific technical question they'll have a real opinion on",
                "Invite them to share how they solved the same problem differently",
            ],
            "weak": [
                "Generic 'hope this helped'",
                "Let me know in the comments",
            ],
            "format": "Technical next step — link, question, or invitation to debate",
        },
        "structural_requirements": {
            "problem": "Clear problem statement — why existing solutions fell short",
            "approach": "Explain the reasoning before showing the implementation",
            "code":    "Commented, runnable code examples with error handling",
            "results": "Measurable outcomes: benchmarks, before/after, or observed behavior",
        },
        "tone_range": ["Technical", "Educational", "Direct", "Analytical"],
        "native_behaviors": [
            "Readers skim for the code first — make it readable and complete",
            "Specific numbers and benchmarks build immediate credibility",
            "Honest about limitations and tradeoffs — omitting them destroys trust",
            "Link to references and prior work — show you've read the landscape",
        ],
        "failure_conditions": [
            "Pseudocode that skips the parts that are actually hard",
            "Claims without benchmarks or reproducible evidence",
            "Missing error handling in examples",
            "Solution presented without problem context",
            "Ignoring edge cases",
        ],
        "validation": {
            "requires_title": True,
            "max_para_words": 150,
            "requires_cta":   False,
        },
    },

    "educational_content": {
        "id": "educational_content",
        "label": "Educational Content",
        "aliases": ["educational", "educational content", "explainer", "how-to", "tutorial"],
        "format": {
            "max_words":     1500,
            "optimal_words": 900,
            "paragraph_style": "Short and scannable, with clear learning progression",
            "hashtags": {"required": False, "min": 0, "max": 0},
            "sections": ["learning_objective", "concept_explanation", "examples", "summary"],
        },
        "hook_rules": {
            "what_works": [
                "State exactly what the reader will know or be able to do after reading",
                "Acknowledge the confusion or misconception you're resolving",
                "Start with the most important concept, not the background",
            ],
            "what_fails": [
                "Starting with the history of the concept",
                "Overwhelming prerequisites before getting to the point",
                "Starting with a definition",
            ],
            "max_words": 80,
        },
        "cta_rules": {
            "strong": [
                "Point to the next concept to learn in the progression",
                "Offer a practice exercise or challenge",
                "Ask them to apply the concept to their own situation",
            ],
            "weak": [
                "Generic 'let me know if this helped'",
                "Subscribe for more content",
            ],
            "format": "Clear next step in the learning journey",
        },
        "structural_requirements": {
            "objective":   "State what they'll learn in the first 2 sentences",
            "explanation": "Simple before complex — build incrementally",
            "examples":    "Concrete before abstract — show it working before explaining why",
            "summary":     "One sentence capturing the core lesson",
        },
        "tone_range": ["Educational", "Conversational", "Professional"],
        "native_behaviors": [
            "Concrete examples before abstract principles — always",
            "Progressive complexity — don't overwhelm in the first paragraph",
            "Analogies bridge from the familiar to the unfamiliar",
            "Clear next steps give momentum",
        ],
        "failure_conditions": [
            "Assumes knowledge the target reader doesn't have",
            "Abstract without concrete examples",
            "No clear learning objective stated",
            "Condescending or using 'obviously' and 'simply'",
        ],
        "validation": {
            "requires_cta": False,
            "max_words":    1500,
        },
    },
}

_DEFAULT_PLATFORM = {
    "id": "general",
    "label": "General Content",
    "aliases": [],
    "format": {
        "max_words":     600,
        "optimal_words": 350,
        "hashtags": {"required": False, "min": 0, "max": 0},
        "sections": ["hook", "body", "conclusion"],
    },
    "hook_rules": {
        "what_works": ["A specific, relevant opening that earns the read"],
        "what_fails":  ["Generic openers that could apply to any topic"],
        "max_words": 50,
    },
    "cta_rules": {
        "strong": ["One clear, specific action"],
        "weak":   ["Vague requests for engagement"],
        "format": "Single clear ask",
    },
    "structural_requirements": {},
    "tone_range": ["Professional", "Conversational", "Direct"],
    "native_behaviors": [],
    "failure_conditions": ["Generic content with no specific point of view"],
    "validation": {"requires_cta": False},
}


def get_profile(use_case: str) -> dict:
    """Match a use case string to a platform profile."""
    if not use_case:
        return _DEFAULT_PLATFORM

    use_case_lower = use_case.lower().strip()

    if use_case_lower in PROFILES:
        return PROFILES[use_case_lower]

    for profile in PROFILES.values():
        for alias in profile.get("aliases", []):
            if alias in use_case_lower or use_case_lower in alias:
                return profile

    return _DEFAULT_PLATFORM


def list_platforms() -> list[str]:
    return [p["label"] for p in PROFILES.values()]


def list_platform_ids() -> list[str]:
    return list(PROFILES.keys())
