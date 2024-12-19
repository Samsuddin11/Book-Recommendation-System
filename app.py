from flask import Flask, render_template, request
import pickle
import numpy as np

# Load the pickled data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    # Step 1: Search the entire `books` dataset for the book title
    searched_book = books[books['Book-Title'].str.contains(user_input, case=False, na=False, regex=False)]


    # If book is found in the books dataset
    if not searched_book.empty:
        # Fetch book details
        book_title = searched_book['Book-Title'].values[0]
        book_author = searched_book['Book-Author'].values[0]
        book_image = searched_book['Image-URL-M'].values[0]
        
        # Step 2: Display the found book
        data = [[book_title, book_author, book_image]]

        # Step 3: Also suggest similar books if the book is present in the pivot table (`pt`)
        if book_title in pt.index:
            index = np.where(pt.index == book_title)[0][0]
            similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]
            for i in similar_items:
                temp_df = books[books['Book-Title'] == pt.index[i[0]]]
                if not temp_df.empty:
                    similar_book = []
                    similar_book.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
                    similar_book.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
                    similar_book.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
                    data.append(similar_book)

        return render_template('recommend.html', data=data)

    else:
        # If book is not found in the dataset
        return render_template('recommend.html', message="Book not found. Please try another book.")

if __name__ == '__main__':
    app.run(debug=True)
    #Samsuddin Khan
