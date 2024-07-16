# 使用

## 命令行

直接通过命令行进行调用。

```sh
$ peth -c eth --cmd erc20 0xdAC17F958D2ee523a2206206994597C13D831ec7
Name: Tether USD
Symbol: USDT
decimals: 6
totalSupply: 48999156520373530
```

查看完整命令行选项
```sh
$ peth -h
```

## 控制台

进入 peth 控制台。

```
Welcome to the peth shell. Type `help` to list commands.

peth > erc20 0xdAC17F958D2ee523a2206206994597C13D831ec7
Name: Tether USD
Symbol: USDT
decimals: 6
totalSupply: 48999156520373530
```

控制台中的命令均可以通过 `peth --cmd` 通过命令行调用。

可通过 `help` 命令查看命令帮助。
```
peth > help

Documented commands (type help <topic>):
========================================
4byte             contract         estimate_gas  name       safe      tx_replay
abi4byte          debank           eth_call      open       send_tx   txs      
abi_decode        debug            exit          oracle     sender    url      
abi_encode        decompile        factory       owner      sh        verify   
address           deth             graph         pair       signer    view     
aes               diff             help          price      status  
aml               diffasm          idm           proxy      storage 
call              disasm           int           proxy_all  time    
chain             download_json    ipython       py         timelock
common_addresses  download_source  keccak256     rpc_call   tx      
config            erc20            log           run        tx_raw  

peth > help erc20

        erc20 <address> : print ERC20 information.
        erc20 <address> <function> <args> : call ERC20 function.
```

## 脚本

通过脚本使用 peth python 库，示例：

```sh
➜ ipython
Python 3.10.0 (default, Oct 29 2021, 11:06:42) [Clang 13.0.0 (clang-1300.0.29.3)]
Type 'copyright', 'credits' or 'license' for more information
IPython 7.28.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: from peth import Peth

In [2]: p = Peth.get_or_create('eth')

In [3]: p.call_contract('0xdAC17F958D2ee523a2206206994597C13D831ec7', 'name')
Out[3]: 'Tether USD'

In [4]: p.call_contract('0xdAC17F958D2ee523a2206206994597C13D831ec7', 'name()->(string)')
Out[4]: 'Tether USD'
```

