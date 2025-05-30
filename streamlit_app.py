import streamlit as st
import json
import os
import random

# ---------------------
# File paths
QUESTION_FILE = "questions.json"
WRONG_ANSWER_FILE = "wrong_answers.json"

# ---------------------
# Load/save functions
def load_flashcards(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_wrong_answers(wrong_counts):
    with open(WRONG_ANSWER_FILE, 'w', encoding='utf-8') as f:
        json.dump(wrong_counts, f)

def load_wrong_answers():
    if os.path.exists(WRONG_ANSWER_FILE):
        with open(WRONG_ANSWER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# ---------------------
def main():
    st.title("📘 SAP Flashcard Practice App")

    flashcards = load_flashcards(QUESTION_FILE)
    mode = st.sidebar.radio("Select Mode", [
        "Practice Mode",
        "Test Mode",
        "Bundle Practice Mode",
        "Mistake Review Mode",
        "Wrong Answer Practice Mode",
        "Full Review Mode"
    ])

    if mode == "Practice Mode":
        if "practice_index" not in st.session_state:
            st.session_state.practice_index = 0
            random.shuffle(flashcards)

        card = flashcards[st.session_state.practice_index]
        st.subheader(f"Question {st.session_state.practice_index + 1} of {len(flashcards)}")
        st.write(card["question"])
        st.markdown(f"**{card.get('instruction', '')}**")

        selected = []
        for key, val in card["options"].items():
            if st.checkbox(f"{key}. {val}", key=f"practice_{key}"):
                selected.append(key)

        if st.button("Submit Answer"):
            correct = set(card["answers"])
            chosen = set(selected)
            if correct == chosen:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Correct answer(s): {', '.join(correct)}")
                wrong_counts = load_wrong_answers()
                qid = str(st.session_state.practice_index)
                wrong_counts[qid] = wrong_counts.get(qid, 0) + 1
                save_wrong_answers(wrong_counts)

        if st.button("Next Question"):
            st.session_state.practice_index += 1
            if st.session_state.practice_index >= len(flashcards):
                st.success("🎉 You have completed all questions!")
                st.session_state.practice_index = 0

    elif mode == "Test Mode":
        test_sample = random.sample(flashcards, min(100, len(flashcards)))
        st.subheader("Complete All Questions Then Submit")
        answers = {}

        for i, card in enumerate(test_sample):
            st.markdown(f"### Question {i+1}: {card['question']}")
            st.markdown(f"**{card.get('instruction', '')}**")
            selected = []
            for key, val in card["options"].items():
                if st.checkbox(f"{key}. {val}", key=f"test_{i}_{key}"):
                    selected.append(key)
            answers[i] = selected

        if st.button("Submit All"):
            score = 0
            wrong_counts = load_wrong_answers()
            for i, card in enumerate(test_sample):
                correct = set(card["answers"])
                chosen = set(answers.get(i, []))
                if correct == chosen:
                    score += 1
                else:
                    qid = str(flashcards.index(card))
                    wrong_counts[qid] = wrong_counts.get(qid, 0) + 1
            save_wrong_answers(wrong_counts)
            st.success(f"✅ Final Score: {score} / {len(test_sample)}")
            st.info("Mistakes saved for review mode.")

    elif mode == "Bundle Practice Mode":
        bundle_sample = random.sample(flashcards, 5)
        st.subheader("5 Random Questions for Quick Practice")
        bundle_answers = {}

        for i, card in enumerate(bundle_sample):
            st.markdown(f"### Question {i+1}: {card['question']}")
            st.markdown(f"**{card.get('instruction', '')}**")
            selected = []
            for key, val in card["options"].items():
                if st.checkbox(f"{key}. {val}", key=f"bundle_{i}_{key}"):
                    selected.append(key)
            bundle_answers[i] = selected

        if st.button("Submit Bundle"):
            score = 0
            wrong_counts = load_wrong_answers()
            for i, card in enumerate(bundle_sample):
                correct = set(card["answers"])
                chosen = set(bundle_answers.get(i, []))
                if correct == chosen:
                    score += 1
                else:
                    qid = str(flashcards.index(card))
                    wrong_counts[qid] = wrong_counts.get(qid, 0) + 1
            save_wrong_answers(wrong_counts)
            st.success(f"✅ Score for this bundle: {score} / 5")

    elif mode == "Mistake Review Mode":
        wrong_counts = load_wrong_answers()
        if not wrong_counts:
            st.success("🎉 No mistakes to review! You've mastered all questions.")
            return

        st.subheader("Reviewing Your Mistakes")
        sorted_wrongs = sorted(wrong_counts.items(), key=lambda x: -x[1])

        for qid, count in sorted_wrongs:
            idx = int(qid)
            card = flashcards[idx]
            st.markdown(f"### ❌ Question (Missed {count}x): {card['question']}")
            st.markdown(f"**{card.get('instruction', '')}**")
            for key, val in card["options"].items():
                st.markdown(f"{key}. {val}")
            correct = set(card["answers"])
            st.markdown(f"**Correct Answer(s):** {', '.join(correct)}")

    elif mode == "Wrong Answer Practice Mode":
        wrong_counts = load_wrong_answers()
        if not wrong_counts:
            st.success("🎉 No wrong answers to practice! You're all set.")
            return

        wrong_indices = list(map(int, wrong_counts.keys()))
        if "wrong_practice_index" not in st.session_state:
            st.session_state.wrong_practice_index = 0
            random.shuffle(wrong_indices)
            st.session_state.wrong_indices = wrong_indices

        if st.session_state.wrong_practice_index >= len(st.session_state.wrong_indices):
            st.success("✅ You've gone through all wrong questions!")
            st.session_state.wrong_practice_index = 0

        idx = st.session_state.wrong_indices[st.session_state.wrong_practice_index]
        card = flashcards[idx]
        st.subheader(f"Wrong Question Practice {st.session_state.wrong_practice_index + 1} of {len(wrong_indices)}")
        st.write(card["question"])
        st.markdown(f"**{card.get('instruction', '')}**")

        selected = []
        for key, val in card["options"].items():
            if st.checkbox(f"{key}. {val}", key=f"wrongpractice_{key}"):
                selected.append(key)

        if st.button("Submit Answer (Wrong Practice)"):
            correct = set(card["answers"])
            chosen = set(selected)
            if correct == chosen:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Correct answer(s): {', '.join(correct)}")
                wrong_counts[str(idx)] = wrong_counts.get(str(idx), 0) + 1
                save_wrong_answers(wrong_counts)

        if st.button("Next Wrong Question"):
            st.session_state.wrong_practice_index += 1

    elif mode == "Full Review Mode":
        st.subheader("📖 Full Review of All Questions with Answers")
        for i, card in enumerate(flashcards):
            st.markdown(f"### Question {i+1}: {card['question']}")
            st.markdown(f"**{card.get('instruction', '')}**")
            for key, val in card["options"].items():
                st.markdown(f"{key}. {val}")
            correct = set(card["answers"])
            st.markdown(f"**Correct Answer(s):** {', '.join(correct)}")

if __name__ == "__main__":
    main()
