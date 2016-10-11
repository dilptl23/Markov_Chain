Below are instructions on how to Tweet Results.

The function generate_tweet can be used just like generate_file. Calling generate_tweet(self, amount) will tweet ‘amount’ many tokens to the twitter handle @dilan_tests. 

EXAMPLE: 

rw = RandomWriter(1, Tokenization.word)
rw.train_iterable("Iterate over this.")
rw.generate_tweet(10)

