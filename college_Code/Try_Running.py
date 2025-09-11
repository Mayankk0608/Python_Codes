import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")

passage = input("Enter a passage: ")
print(f"\nOriginal Passage:\n {passage}")

words = word_tokenize(passage)
stop_words = set(stopwords.words("english"))
filtered_words = [word for word in words if word.lower() not in stop_words]
cleaned_passage = " ".join(filtered_words)

print(f"\nPassage after removing stop words:\n {cleaned_passage}")