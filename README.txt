Below are instructions on how to test Twitter extra credit. I did not do the full extra credit. 

The function generate_tweet can be used just like generate_file. Calling generate_tweet(self, amount) will tweet ‘amount’ many tokens to the twitter handle @dilan_tests. 

EXAMPLE: 

rw = RandomWriter(1, Tokenization.word)
rw.train_iterable("Iterate over this.")
rw.generate_tweet(10)

