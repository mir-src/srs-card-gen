# 🃏 srs-card-gen

## 📝 Description
**srs-card-gen** is a powerful Python-based web application built with **Streamlit**. It streamlines the process of creating flashcards for Spaced Repetition Systems (SRS) like Anki. 

Whether you want to leverage high-speed cloud AI via **Groq**, run things privately with **Local AI (Ollama)**, or keep total control with **Manual Entry**, this app adapts to your workflow.

---

## ✨ Features
- 🚀 **AI Generation:** Instant card creation using the Groq API.
- 🏠 **Local First:** Support for Ollama for private, offline card generation.
- 🎨 **User Friendly:** A clean Streamlit interface designed for speed.
- 🛠️ **Manual Mode:** Fine-tune your cards exactly how you want them.

---

## ⚙️ Installation

Follow these steps to get the environment running on your local machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mir-src/srs-card-gen.git](https://github.com/mir-src/srs-card-gen.git)
   cd srs-card-gen

2. **pip install -r requirements.txt**

3. **Set up your environment variables:**
Create a **.env** file in the root directory and add your Groq key: GROQ_API_KEY=your_key_here

4. **Launch the app:**
   ```bash
   streamlit run app.py

---

## To-Do:
- [x] Make database related files
- [x] Add FSRS math logic into the app
- [x] Finish making the blueprints for objects
- [x] Included Ollama Local AI
- [x] Add Groq AI functionality
- [ ] Add TTS for language flashcards
- [ ] Make the UI with Streamlit
- [ ] Add custom CSS for styling

**Current Update**: Implemented the groq AI functionality, updated the logic for AI generated flashcards (general knowledge type of card for now), added a safe way to delete media together with cards, decks and users, we no longer have orphaned media when we delete a card for example, media gets deleted together with the database table. Fixed an issue where if we change the name of a card the audio file of that specific card doesn't know that we changed the name of the card, now we delete the audio file if that's the case.

---

## Author
**mir-src**
- 📧 Contact: [264200162+mir-src@users.noreply.github.com](mailto:264200162+mir-src@users.noreply.github.com)
- Python & C++ Developer 🐍
- 2D Illustrator 🎨