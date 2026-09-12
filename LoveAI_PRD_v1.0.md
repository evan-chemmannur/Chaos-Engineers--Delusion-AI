# LoveAI — Product Requirements Document

**Version:** 1.0  
**Status:** Proposed  
**Platform:** Windows Desktop  
**Language:** Python 3

## 1. Product Overview

LoveAI is an AI-powered relationship companion focused on entertainment-oriented compatibility analysis and respectful communication guidance.

The application combines five core features:

1. 💘 Compatibility Analyzer
2. 📸 Image Similarity
3. 🤖 AI Relationship Advisor
4. 💬 AI Message Assistant
5. ❤️ Relationship Journey

The project demonstrates Python, GUI development, computer vision, LLM/API integration, prompt engineering, SQLite, OOP, and modular software architecture.

LoveAI must never claim to scientifically predict romantic compatibility or another person's feelings.

---

## 2. Goals

- Build a polished Python desktop application.
- Integrate an external LLM for personalized guidance.
- Demonstrate computer vision using OpenCV.
- Provide useful AI-powered message assistance.
- Track relationship milestones using SQLite.
- Use a clean, modular architecture.
- Protect API credentials.
- Handle API and application errors gracefully.
- Package the application as a Windows executable.

---

## 3. Core Features

### 3.1 💘 Compatibility Analyzer

Users enter:

- Their name
- Other person's name
- Shared interests

The system calculates:

- Name compatibility score
- Shared-interest score
- Combined entertainment score

Example:

```text
Name Compatibility     85%
Shared Interests        92%
Entertainment Score     88%
```

Result example:

```text
💕 Compatibility Score

88%

Great Match!
```

The score must be deterministic for the same inputs.

Required disclaimer:

> Compatibility scores are for entertainment purposes only and do not scientifically predict relationship success or another person's feelings.

---

### 3.2 📸 Image Similarity

Users upload two local images.

Processing:

```text
Image 1 ─┐
         ├─> Preprocessing ─> Visual Comparison ─> Similarity %
Image 2 ─┘
```

Possible techniques:

- Resizing
- Normalization
- Color histogram comparison
- Pixel similarity
- ORB feature matching

Implementation belongs in:

```text
app/core/image_comparator.py
```

Result:

```text
📸 Visual Similarity

82%

High Visual Similarity
```

Required disclaimer:

> This feature measures visual similarity only. It does not identify people or determine attraction, personality, romantic compatibility, or relationship probability.

The first version must not implement face identification or sensitive-trait inference.

Image processing should remain local whenever practical.

---

### 3.3 🤖 AI Relationship Advisor

This is the primary feature of LoveAI.

The user provides:

**Current relationship**
- Stranger
- Classmate
- Acquaintance
- Friend
- Close Friend
- Already talking

**Communication frequency**
- Rarely
- Sometimes
- Often
- Daily

**Common interests**
- Music
- Football
- Movies
- Gaming
- Other custom interests

**Goal**
- Start talking
- Become better friends
- Spend more time together
- Ask them to hang out
- Express feelings
- Ask them on a date
- Improve an existing relationship

**Situation**

A free-text description of what is happening.

The application sends this context to an LLM.

Architecture:

```text
User Context
     ↓
Prompt Builder
     ↓
System Instructions
     ↓
LLM API
     ↓
Response Validation
     ↓
Personalized Roadmap
```

Example output:

```text
🤖 YOUR PERSONALIZED ROADMAP

01 — Start natural conversations
02 — Build familiarity
03 — Look for mutual effort
04 — Suggest a casual activity
05 — Communicate honestly
06 — Respect their response
```

The LLM must:

- Encourage genuine communication.
- Respect consent and boundaries.
- Acknowledge uncertainty.
- Avoid claiming certainty about another person's feelings.
- Avoid manipulation.
- Avoid coercion.
- Avoid harassment or stalking.
- Avoid repeated unwanted contact.
- Never guarantee a romantic outcome.

---

### 3.4 💬 AI Message Assistant

This feature combines message analysis and message improvement.

#### Analyze Mode

User pastes a message.

The AI analyzes:

- Tone
- Clarity
- Pressure
- Naturalness
- Potential awkwardness
- Possible ambiguity

Example:

```text
MESSAGE ANALYSIS

Tone          Friendly
Clarity       High
Pressure      Low
Naturalness   Good

AI Feedback:
The message is friendly and clear, but
could be made slightly more natural.
```

The AI must not claim to know what the recipient feels.

#### Improve Mode

User enters a message and selects:

- Casual
- Friendly
- Funny
- Confident
- Sweet
- Direct
- Short

The LLM generates multiple alternatives.

Each result should provide:

- Copy
- Regenerate
- Save

---

### 3.5 ❤️ Relationship Journey

Users manually track relationship milestones.

Example:

```text
❤️ YOUR JOURNEY

✓ First Conversation
      ↓
✓ Became Friends
      ↓
✓ Started Talking Regularly
      ↓
○ First Hangout
      ↓
○ Expressed Feelings
      ↓
○ Asked Them Out
```

Each milestone can contain:

- Title
- Description
- Date
- Completion status
- Notes

Users can:

- Add milestone
- Edit milestone
- Complete milestone
- Delete milestone
- Add notes

Example progress:

```text
Journey Progress

3 / 6 milestones

██████████░░░░░░░░
```

Journey data must be stored in SQLite.

---

## 4. Dashboard

The Dashboard provides an overview of all five core features.

Example:

```text
LOVEAI
Understand. Communicate. Connect. 💕

Compatibility
88%

Name Match        85%
Shared Interests  92%

[ View Analysis ]

AI Advisor
Get personalized guidance for your situation.

[ Ask AI ]

Message Assistant
Analyze or improve your next message.

[ Open Assistant ]

Journey
3 / 6 milestones completed

[ View Journey ]
```

---

## 5. Navigation

Main sidebar:

```text
💕 LoveAI

🏠 Dashboard
💘 Compatibility
📸 Image Similarity
🤖 AI Advisor
💬 Message Assistant
❤️ Journey

──────────────

⚙️ Settings
```

---

## 6. UI/UX Requirements

The application should look like a premium modern AI product rather than a traditional love calculator.

### Visual Style

- Dark-first interface
- Near-black/charcoal background
- Subtle pink and purple accents
- Soft gradients
- Rounded cards
- Minimal glassmorphism
- Modern sans-serif typography
- Premium AI SaaS aesthetic
- Subtle animations

Avoid:

- Excessive hearts
- Rose graphics
- Bright red romance themes
- Cartoon styling
- Excessive animations
- Cluttered layouts

### Reusable Components

- Sidebar
- Header
- Cards
- Buttons
- Inputs
- Textareas
- Dropdowns
- Tag inputs
- Progress bars
- Circular score
- AI message bubbles
- Upload cards
- Result cards
- Timeline
- Milestone cards
- Loading indicators
- Error messages
- Toast notifications

---

## 7. Required UI States

Each major feature should support:

1. Empty state
2. Input state
3. Loading state
4. Success state
5. Error state

AI loading example:

```text
🤖 AI is thinking...

Analyzing your situation...
```

Error example:

```text
Unable to connect to the AI service.

Check your API configuration and try again.
```

---

## 8. AI Architecture

AI code must be separated from the GUI.

```text
CustomTkinter GUI
       ↓
AI Service Layer
       ↓
Prompt Builder
       ↓
LLM Provider
       ↓
Response Validator
       ↓
GUI
```

Recommended files:

```text
app/ai/
├── ai_advisor.py
├── prompt_builder.py
└── message_assistant.py
```

The LLM provider should be replaceable without rewriting the GUI.

---

## 9. Prompt Architecture

Each AI feature should use structured prompts.

```text
System Instructions
        +
Feature Instructions
        +
User Context
        ↓
       LLM
        ↓
Structured Response
```

The system prompt should define:

- AI role
- Safety boundaries
- Tone
- Output structure
- Uncertainty requirements

The user prompt should contain only information needed for the selected feature.

---

## 10. Database

Use SQLite for local persistence.

### compatibility_results

```text
id
name1
name2
name_score
interest_score
combined_score
created_at
```

### journey_milestones

```text
id
title
description
completed
event_date
notes
created_at
```

### ai_history

```text
id
feature_type
input_summary
response
created_at
```

AI history should be optional and controlled through Settings.

---

## 11. Privacy

- Image similarity should be performed locally.
- Only necessary text/context should be sent to an external LLM.
- Clearly indicate when information is sent to an external AI provider.
- API keys must never be hard-coded.
- Store API credentials in `.env`.
- `.env` must be included in `.gitignore`.

Example:

```text
LLM_API_KEY=your_api_key_here
```

---

## 12. Technical Stack

| Component | Technology |
|---|---|
| Language | Python 3 |
| GUI | CustomTkinter |
| Image Processing | OpenCV |
| Numerical Processing | NumPy |
| Image Handling | Pillow |
| AI | External LLM API |
| API Communication | requests / provider SDK |
| Database | SQLite |
| Environment Variables | python-dotenv |
| Packaging | PyInstaller |
| Version Control | Git + GitHub |

Optional:

```text
SQLAlchemy
```

---

## 13. Project Structure

```text
LoveAI/
│
├── main.py
│
├── app/
│   ├── __init__.py
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── compatibility_view.py
│   │   ├── image_view.py
│   │   ├── advisor_view.py
│   │   ├── message_view.py
│   │   ├── journey_view.py
│   │   └── settings_view.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── calculator.py
│   │   ├── image_comparator.py
│   │   ├── compatibility.py
│   │   └── validation.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── ai_advisor.py
│   │   ├── prompt_builder.py
│   │   └── message_assistant.py
│   │
│   └── database/
│       ├── __init__.py
│       └── database.py
│
├── assets/
│   ├── logo.png
│   └── icons/
│
├── database/
│   └── loveai.db
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 14. Development Phases

### Phase 1 — Setup

- Create Git repository.
- Create Python virtual environment.
- Create folder structure.
- Configure `.gitignore`.
- Install dependencies.
- Create `main.py`.

### Phase 2 — GUI

- Create CustomTkinter window.
- Build sidebar.
- Build dashboard.
- Implement navigation.
- Create reusable components.

### Phase 3 — Compatibility

- Implement name calculator.
- Implement shared-interest scoring.
- Add validation.
- Build compatibility UI.
- Add disclaimer.

### Phase 4 — Image Similarity

- Implement image upload.
- Implement preprocessing.
- Implement visual similarity.
- Add image preview.
- Display results.
- Add disclaimer.

### Phase 5 — Database

- Create SQLite database.
- Implement milestone CRUD.
- Implement optional history.
- Connect database to GUI.

### Phase 6 — LLM Integration

- Select LLM provider.
- Configure API key.
- Create AI service.
- Create prompt builder.
- Implement error handling.

### Phase 7 — AI Advisor

- Build questionnaire.
- Generate personalized roadmap.
- Display AI response.
- Add copy/regenerate actions.

### Phase 8 — Message Assistant

- Implement message analysis.
- Implement message improvement.
- Add tone/style selection.
- Add copy/regenerate actions.

### Phase 9 — Journey

- Implement milestone timeline.
- Add progress indicator.
- Implement CRUD.
- Connect to SQLite.

### Phase 10 — Polish and Testing

- Add loading states.
- Add error states.
- Improve UI.
- Test API failures.
- Test image processing.
- Test database operations.
- Test all navigation.

### Phase 11 — Packaging

- Configure PyInstaller.
- Build Windows executable.
- Test on a clean machine.
- Prepare documentation.

---

## 15. Testing Requirements

### Compatibility

Test:

- Empty names
- Long names
- Special characters
- Repeated identical inputs
- Different interests

### Image Similarity

Test:

- Identical images
- Similar images
- Different images
- Invalid files
- Unsupported formats
- Very large images

### AI

Test:

- Missing API key
- Invalid API key
- Network failure
- Timeout
- Empty situation
- Unexpected response

### Database

Test:

- Add milestone
- Edit milestone
- Complete milestone
- Delete milestone
- Persistence after application restart

---

## 16. Security Requirements

The application must:

- Never hard-code API keys.
- Validate user input.
- Use parameterized SQL queries.
- Never execute LLM-generated code.
- Safely handle uploaded files.
- Restrict image processing to supported formats.
- Avoid unnecessary transmission of personal data.

---

## 17. Success Criteria

The project is successful when:

- The application launches reliably.
- All five core features work.
- The UI is consistent and polished.
- Compatibility results are deterministic.
- Image similarity works locally.
- AI Advisor generates personalized LLM responses.
- Message Assistant analyzes and improves messages.
- Journey milestones persist in SQLite.
- API failures are handled gracefully.
- API keys remain secure.
- The application can be packaged as a Windows executable.

---

## 18. College Demonstration Flow

Recommended demo:

```text
1. Launch LoveAI
        ↓
2. Calculate compatibility
        ↓
3. Compare two images
        ↓
4. Open AI Relationship Advisor
        ↓
5. Enter a realistic situation
        ↓
6. Generate personalized roadmap
        ↓
7. Open Message Assistant
        ↓
8. Analyze and improve a message
        ↓
9. Add relationship milestones
        ↓
10. Show saved journey progress
```

This demonstrates:

- Python
- OOP
- GUI development
- Computer Vision
- LLM/API integration
- Prompt Engineering
- NLP
- SQLite
- Modular architecture

---

## 19. Future Enhancements

Possible future versions:

- Web application
- Mobile application
- Voice input
- Voice AI responses
- Local/offline LLM
- PDF export
- Multiple LLM providers
- Multilingual support
- Cloud synchronization
- Advanced visual similarity

These are outside the Version 1.0 scope.

---

## 20. Final Product Definition

LoveAI is a focused AI-powered relationship companion built around five capabilities:

```text
             💕 LOVEAI

     ┌──────────────────────┐
     │ 💘 Compatibility      │
     ├──────────────────────┤
     │ 📸 Image Similarity   │
     ├──────────────────────┤
     │ 🤖 AI Relationship    │
     │    Advisor            │
     ├──────────────────────┤
     │ 💬 AI Message         │
     │    Assistant          │
     ├──────────────────────┤
     │ ❤️ Relationship       │
     │    Journey            │
     └──────────────────────┘
```

The AI Relationship Advisor is the centerpiece. The other four features provide complementary functionality while keeping the project technically diverse and manageable.

---

## 21. Tagline

**LoveAI — Understand. Communicate. Connect. 💕**

---

## 22. Product Disclaimer

LoveAI is an entertainment and communication-support application.

Its compatibility scores are not scientifically validated relationship predictions. Image similarity represents visual similarity only. AI-generated guidance is advisory and cannot determine another person's thoughts, emotions, attraction, or future actions.

Users should always respect consent, personal boundaries, privacy, and the other person's decisions.
