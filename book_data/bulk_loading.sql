
.mode csv
.separator ","
.import '| tail -n +2 ./book_data/books.csv' RawBooks
.import '| tail -n +2 ./book_data/book_tags.csv' RawBookTags
.import '| tail -n +2 ./book_data/tags.csv' RawTags