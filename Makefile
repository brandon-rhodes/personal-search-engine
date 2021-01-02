Examples/twitter-likes-example.txt: Cache/7b02ee57e98a14732cefac8930b3f1d4
	python save_tweets.py $< > tmp
	mv tmp $@

big: Documents/twitter-likes

Documents/twitter-likes: save_tweets.py Indexes/twitter-likes
	python save_tweets.py $$(cat Indexes/twitter-likes | sed 's:^:Cache/:') > tmp
	mv tmp $@

big: Documents/twitter-my-tweets

Documents/twitter-my-tweets: save_tweets.py Indexes/twitter-my-tweets
	python save_tweets.py $$(cat Indexes/twitter-my-tweets | sed 's:^:Cache/:') > tmp
	mv tmp $@
