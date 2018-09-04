# drunkard CLI

It intent to send files in a directory to the [server](https://github.com/cadicallegari/drunkard-server-go)


## Installation

After clone the respository

```
make install
```


## Usage

A example of how to use:

```
drunkard-cli -h http://localhost:8080/records -d tests/testdata/
```

you could find more options running the help command

```
drunkard-cli --help
```


to run along with the server, plese check out [here](https://github.com/cadicallegari/drunkard-server-go/blob/master/README.md#run-locally) how to server run.



# Contributing

Recommended to create a new virtualenv

```
make init
```


## Testing

```
make test
```
