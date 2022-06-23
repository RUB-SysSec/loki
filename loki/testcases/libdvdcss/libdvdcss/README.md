# Obfuscation Test:

Use `./install-modified-libdvdcss.sh` to build both obfuscated and unobfuscated libdvdcss.

libdvdcss commit: `ba96b4b2aabf046b4de762781e1fcaa76e7a3b7e`

# Goals and feature

**Libdvdcss** is a portable abstraction **lib**rary for **DVD** decryption.

It is part of the **VideoLAN** project, which among other things produces **VLC**, a full video client/server streaming solution. 

**VLC** can  also be used as a standalone program to **play video streams** from a hard disk or a DVD.


**Libdvdcss** currently supported platforms are **GNU/Linux**, **FreeBSD**, **NetBSD**, **OpenBSD**, **Haiku**, **Mac OS X**, **Solaris**, **QNX**, **OS/2**, and **Windows NT 4.0 SP4** (with IE 5.0) or later.

## Building and installing instructions for Libdvdcss

See the [INSTALL file](https://code.videolan.org/videolan/libdvdcss/-/blob/master/INSTALL) for full instructions.


## Running libdvdcss


The behavior of the library can be changed by setting two environment variables :

`DVDCSS_METHOD={title|disc|key}`: method for **key decryption** :

- **title** : By default the decrypted title key is guessed from the encrypted
              sectors of the stream. Thus it should work with a file as well as
              the DVD device. But decrypting a title key may take too much time
              or even fail. With the **title method**, the key is only checked at
              the **beginning of each title**, so it will not work if the key
              changes in the middle of a title.

- **disc** :  The disc key is **cracked first**. Afterwards all title keys can be
              decrypted **instantly**, which allows checking them often.

- **key** :   The same as the "disc" method if you do not have a file with player
              keys at compile time. If you do, disc key decryption will be faster.
              This is the **default method** also employed by libcss.

 
`DVDCSS_VERBOSE={0|1|2}`: libdvdcss **verbosity**

- **0**: no error messages, no debug messages (this is the default)
- **1**: only error messages
- **2**: error and debug messages


## Troubleshooting


A **mailing-list** has been set up for support and discussion about
libdvdcss. Its address is:

   <libdvdcss-devel@videolan.org>

To subscribe or unsubscribe, go [here](http://mailman.videolan.org/).


When reporting **bugs**, try to be as **precise** as possible (which OS, which
distribution, what plugins you were trying, and so on).

## CoC

The [VideoLAN Code of Conduct](https://wiki.videolan.org/CoC) applies to this project.

## Licence

**Libdvdcss** is released under the **General Public License**, ensuring it will stay free, and used only for free software products.

## Resources


The [VideoLAN web site](http://www.videolan.org/) is a good start for
information about MPEG and DVD playback. 

Have a look at the [support section](https://www.videolan.org/support/) to look for answers.

You can also have a look to [the documentation](https://videolan.videolan.me/libdvdcss/).
