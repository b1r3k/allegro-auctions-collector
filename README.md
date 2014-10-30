# allegro auctions collector

Objective: to harvest auctions data from Allegro auction system (most popular one in Poland) in long time frames

Applications allows to:
 - collect all active auctions in given auction category
 - update state (how many items sold, how many bids, etc.) of previously collected auctions

The idea was to play a little bit with few concepts:
 - Python coroutines
 - data exchange through pipelines
 - modularization enforced through usage of piplines

*Disclaimer*: It's proof of concept application, it could be solid base but on it's own it's not intended as production ready.

## Usage

### API access

Obtain API keys from Allegro [^1] and put them in config.py

`
user = AllegroUser('LOGIN',
                    'PASSWORD',
                    'APIKEY'
)
`

### Fetch auctions

`$ python src/main.py -c 16447 -f > ramy.csv`

### Update auctions state & add new ones

`$ cat ramy.csv | python src/main.py -u > ramy2.csv`

## License

Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License

## References

[^1]: http://allegro.pl/webapi/?lang=en