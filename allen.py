from allennlp.predictors import predictor
coref = predictor.Predictor.from_path('https://s3-us-west-2.amazonaws.com/allennlp/models/coref-model-2018.02.05.tar.gz')
s= "Shelfari users built virtual bookshelves of the titles which Shelfari users owned or had read and Shelfari users could rate review tag and discuss Shelfari users books. Users could also create groups that other members could join create discussions and talk about books or other topics. Recommendations could be sent to friends on the site for what books to read. Amazon bought the company in August 2008."


json = coref.predict('Shelfari users built virtual bookshelves of the titles which Shelfari users owned or had read and Shelfari users could rate review tag and discuss Shelfari users books. Users could also create groups that other members could join create discussions and talk about books or other topics. Recommendations could be sent to friends on the site for what books to read. Amazon bought the company in August 2008.')

print(json)
for i in json['clusters']:
    for j in i:
        print(json['document'][j[0]], json['document'][j[1]])
