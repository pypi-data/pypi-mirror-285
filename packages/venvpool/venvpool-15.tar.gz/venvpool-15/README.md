# venvpool
Run your Python scripts using an automated pool of virtual environments to satisfy their requirements

## Commands

### motivate
Create and maintain wrapper scripts in ~/.local/bin for all runnable modules in the given projects, or the current project if none given.

### motivate -S
Create/maintain wrappers for all console_scripts of the given requirement specifier.

### motivate -C
Compact the pool of venvs.

## API

<a id="venvpool"></a>

### venvpool

<a id="venvpool.dotpy"></a>

###### dotpy

Python source file extension including dot.

<a id="venvpool.initlogging"></a>

###### initlogging

```python
def initlogging()
```

Initialise the logging module to send debug (and higher levels) to stderr.

