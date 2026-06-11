# EduPulse Study Suite

An AI-first assessment engine built for learners and teams to instantly transform complex, long-form study materials into highly structured, grounded knowledge assessments. 

EduPulse eliminates systemic LLM hallucinations by enforcing absolute context window boundaries, ensuring every question and multiple-choice distractor is derived strictly from the provided source text—never from general training data.

---

## 💡 Executive Summary & Problem Space

* **Information Overload**: Students and professionals face long-form content (notes, articles, slide decks) that is time-consuming to convert into practice material.
* **Inconsistent Assessment Quality**: Manual question authoring yields uneven difficulty, poor coverage, and slow iteration.
* **EduPulse (The Bridge)**: Automates extraction, structures context boundaries, and generates high-accuracy, personalized quizzes instantly to accelerate retention and mastery.

---

## 🛠️ Core User-Facing Features

1.  **Source Material Payload Area**: Robust text extraction with context boundary creation (paragraph and section anchors), multi-format paste support, and automatic noise filtering.
2.  **Generation Tuning**: Customizable question-volume sliders, segmented cognitive difficulty adjustments (Easy → Medium → Hard), and topic-focused seeding for targeted assessments.
3.  **Real-Time Interactive Assessment Dashboard**: Adaptive presentation, immediate scoring feedback, timed sections, and in-line factual trace hints for formative learning loops.
4.  **Post-Assessment Analytics & Portability**: Dynamic dashboards displaying metrics like accuracy percentages alongside data portability high-fidelity exporters (raw CSV logs for data science and printable PDF reports for instructors/stakeholders).

---

## 🏗️ Technical Architecture & System Workflow

The data pipeline transitions seamlessly across four distinct operational layers:

* **Frontend Layer**: Streamlit UI utilizing deterministic state management (`st.session_state`) and targeted CSS injection for uniform dark-orange layout themes.
* **Backend Orchestration**: Localized JSON schemas (`data/quiz_rules.json`) to validate generation rules and drive deterministic parsing.
* **AI Synthesis Layer**: Custom `QuizAPIHandler` orchestrating system prompt templates, structural context windowing, and exponential backoff retry algorithms to seamlessly manage rate limits over the `google-genai` SDK.
* **Persistence & Analytics**: High-fidelity export loops creating formatted CSV runtime data points and structured `fpdf2` PDF performance reports.

---

## 📊 Completed Quality Assurance Matrix

As part of the documentation and verification lifecycle, the system was cross-evaluated against rigorous test benchmarks to verify strict context isolation:

| Test Input | Expected Output | Actual Output | Pass/Fail |
| :--- | :--- | :--- | :--- |
| **DBMS Notes** (Normalization & 1NF/2NF/3NF facts) | 5 MCQs answerable strictly from notes; no outside relational knowledge bleed. | Clean JSON array parsed; options explicitly mapped to context anchors. | **PASS** |
| **Python Core** (Data structures & garbage collection) | 5 Medium questions mapping functional nuances explicitly detailed in text. | Handled successfully; distractors looks highly technical but are textually false. | **PASS** |
| **Short Text Validation** (Input payload dropped below 50 words threshold) | System flags validation error dynamically without sending wasteful API requests. | UI cleanly displayed warning block alert, successfully stopping runtime exceptions. | **PASS** |
| **API Stress Test** (Simulated 429 Rate Limit execution spike) | App remains stable, applies exponential backoff delays, and safely retries. | Caught 429 error code and resolved smoothly using updated 5-second backoff loops. | **PASS** |

---

## 👥 Core Team & Project Roles

* **Shireesha (Member 1)**: Data collection, rules creation, and structuring into JSON files; prompt engineering design benchmarks.
* **Ramya (Member 2 - Frontend)**: Builds the interactive user interface layout, designs custom color sheets, and manages client-side state hooks.
* **Tejaswini (Member 4 - Backend)**: Develops the server-side API handler logic, manages model integrations, and enforces core validation business rules.
* **Pravallika (Member 5 - Testing, Deployment, & Documentation)**: Runs all automated and manual test cases, configures environment cloud hosting secrets, authors technical repository documentation, and coordinates the end-to-end user demo framework.