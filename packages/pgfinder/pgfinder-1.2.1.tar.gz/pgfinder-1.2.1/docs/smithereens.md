# Smithereens

[Smithreens][sm] is written in [rust][rust] and is intended to be used in the [Web Assembly][wass] framework as a backend to
the [PGFinder][pgfinder] WebUI. Its purpose is to take as input a set of monomer building blocks and derive the
molecular mass of Multimers which are built based on user specified structure of Monomer units and crosslinks.

## Integration with PGFinder

[PGFinder][pgfinder] currently consists of two components, a Python library for analysing the mass spectroscopy of
bacterial cell walls and determining the likely structure of constituents and a WebUI written in JavaScript framework
[svelte][svelte] which considerably lowers the barrier to usage. The current deployment of the WebUI can be found
[here][pgfinder_web] (see also [PGFinder documentation][pgfinder_docs]).

The array of peptidoglycans is vast and the purpose of Smithereens is to allow users to specify their own list of
building blocks and target multimers and have these molecular masses serve as input to the current [PGFinder][pgfinder].

Because of the stack (set of software) being used in the project and that it is currently under heavy development
automated deployment is not yet in place. To which end the following steps are required to build the software and
integrate it with the WebUI.

### Pre-requisites

There are a number of pre-requisites to working with Rust. How you install these will depend on your operating system.

+ [Rust][rust]

You may already have this installed system wide (check with `which rustc`) but it is recommended you install under your
user account using [rustup][rustup the repository

Obvious first step but you need a copy of this repository locally in order to build it. You may wish to fork and clone a
copy of your own fork, in which case adjust the URLs appropriately (if you don't have GitHub configured with SSH keys
then use the [HTML](https://github.com/TheLostLambda/smithereens.git) address to clone instead). Development work is
being carried out `wasm-pilot` so you need to switch branches.

``` bash
cd ~/work/git/hub/TheLostLambda
git clone git@github.com:TheLostLambda/smithereens.git
cd smimthereens
git switch wasm-pilot
```

### Building the Package

Rust packages are configured via the `Cargo.toml` which is used by [Cargo][cargo] the Rust package manager to build the
package. This handles downloading dependencies, compiling the package and making binaries that can be used.

Once you are on the correct branch (`wasm-pilot` as of 2024-03-06) it is simple to use Cargo to

``` bash
cargo build
```


### Build the Package for Web Assembly

The [Rust and WebAssembly][rust_wasm] book has a useful tutorial that can inform how to build packages for use in
WebAssembly. First you need to have the [`wasm-pack`][wasm-pack] Rust package installed, you can install this using Cargo.

``` bash
cargo install wasm-pack
```

`wasm-pack` undertakes building the package using `wasm32-unknown-unknown` as a target. This needs to be installed using
[`rustup`][rustup] but not all systems will have this installed as some will have [`rustc`][rustc] installed
instead. There are [instructions][wasm32-unknown-unknown] on how to do this which are shown below (indented lines are output)

``` bash
❱ rustc --version
  rustc 1.76.0 (07dca489a 2024-02-04) (Arch Linux rust 1:1.76.0-1)
❱ mkdir tmp && cd tmp
❱ wget https://static.rust-lang.org/dist/rust-std-1.76.0-wasm32-unknown-unknown.tar.gz
❱ tar xzvf rust-std-1.76.0-wasm32-unknown-unknown.tar.gz
❱ cd rust-std-1.76.0-wasm32-unknown-unknown
❱ rustc --print sysroot
  /usr
```

Under this directory you should find `lib/rustlib` (i.e. in this example the full path is `/usr/lib/rustlib/`) and the
file `rust-std-1.76.0-wasm32-unknown-unknown/rust-std-wasm32-unknown-unknown/lib/rustlib/wasm32-unknown-unknown` needs copying there. Those familiar
with UNIX like operating systems will have recognised that this is a directory that normal users can not access, so you
either need `root` access or to be in the `sudo` group that permits access. The following steps were undertaken as `root`

``` bash
cp -r /home/neil/work/git/hub/TheLostLambda/smithereens/tmp/rust-std-1.76.0-wasm32-unknown-unknown/rust-std-wasm32-unknown-unknown/lib/rustlib/wasm32-unknown-unknown /usr/lib/rustlib/.
```


`wasm-pack` can then be used to build the packages.

``` bash
wasm-pack build
```

**NB** - Currently this fails in some situations the following assumes

### Copying to PGFinder

The package artifacts are located in the `pkg/` directory and it is these that need copying to
`pgfinder/web/src/lib`. The [Hello World!](https://rustwasm.github.io/docs/book/game-of-life/hello-world.html) page
from the Rust and [[WebAssembly][wa] book is informative as to what each file is/does.

``` bash
$ ls -l pkg/
total 5748
-rw-r--r-- 1 neil neil     292 Mar  6 10:44 package.json
-rw-r--r-- 1 neil neil    1574 Mar  6 10:44 README.md
-rw-r--r-- 1 neil neil   10719 Mar  6 10:44 smithereens_bg.js
-rw-r--r-- 1 neil neil 5852244 Mar  6 10:44 smithereens_bg.wasm
-rw-r--r-- 1 neil neil     702 Mar  6 10:44 smithereens_bg.wasm.d.ts
-rw-r--r-- 1 neil neil     352 Mar  6 10:44 smithereens.d.ts
-rw-r--r-- 1 neil neil     160 Mar  6 10:44 smithereens.js
```

| **File**       | **Description**                                                                                                                                       |
|:---------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|
| `*.wasm`       | The WebAssembly binary created from source by the Rust compiler.                                                                                      |
| `*.js`         | "_contains JavaScript glue for importing DOM and JavaScript functions into Rust and exposing a nice API to the WebAssembly functions to JavaScript._" |
| `*.d.ts`       | "_contains TypeScript type declarations for the JavaScript glue._"                                                                                    |
| `package.json` | "_[The package.json file contains metadata about the generated JavaScript and WebAssembly package.](https://docs.npmjs.com/files/package.json)_"      |

Once these files are in place  the next step is to refer to them from the Svelte web-framework

**NB** - currently static files from the
[`TheLostLambda/smithereens@wasm-pilot`](https://github.com/TheLostLambda/smithereens/tree/wasm-pilot/pkg) branch and
_haven't_ created them from source as attempts to do so failed.




### Adding the Uploader - Svelte


**WORK IN PROGRESS** So far we have setup the Rust code, compiled it under [WebASsembly][wa]. We now need to turn to the [Svelte][svelte]
framework and write some code for this to be usable.


[cargo]: https://doc.rust-lang.org/cargo/
[pgfinder]: https://github.com/Mesnage-Org/pgfinder
[pginder_docs]: https://pgfinder.readthedocs.io/en/latest/
[pgfinder_web]: https://mesnage-org.github.io/pgfinder/
[rust]: https://doc.rust-lang.org/stable/book/
[rustc]:
[rustup]: https://www.rust-lang.org/tools/install
[rust_wasm]: https://rustwasm.github.io/docs/book/game-of-life/hello-world.html
[sm]: https://github.com/TheLostLambda/smithereens
[svelte]: https://svelte.dev/docs/introduction
[ts]: https://www.typescriptlang.org/
[wass]: https://webassembly.org/
[wasm-pack]: https://rustwasm.github.io/docs/wasm-pack/
[wasm32-unknown-unknown]: https://rustwasm.github.io/docs/wasm-pack/prerequisites/non-rustup-setups.html
