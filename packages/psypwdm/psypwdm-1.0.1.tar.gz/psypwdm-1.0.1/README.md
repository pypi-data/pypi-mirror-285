# psypwdm

The package `psypwdm` is a freely available, local password manager. 
Note, a running instance of PostgreSQL database is needed for `psypwdm` to function. 
See instructions on downloading and installing PostgreSQL [here](https://www.postgresql.org/).

## Basic structure

**Warning.** *Upon installation, the database initialised and created by `psypwdm` is called `passwordmanager`. 
If this table exists in a running instance of Postgres prior to importing `psypwdm`, then nothing will happen.
Method calls called on `psypwdm` however will aim to modify the `passwordmanager` table.*

The following fields in the `passwordmanager` table are designed for user input:

    - useraccountsystemtype
        - the system hosting the account, such as 'website', 'windows account', etc.
    - username
        - the username for accessing the system
    - password
        - the password to authenticate the user on the system
    - comments
        - any further comments about this entry, e.g., such as hints for the password, description or URL of the system etc.

Unlike the other fields, the password is not stored as plain text. The local password manager 
requests a password for any entry and stores its hash after salting. See the tutorial at the link below
on how to retrieve entries by field name(s) or by password.

## Install

Run the following code to install `psypwdm` locally.

    $ pip install psypwdm

## Tutorial

See a tutorial at the following link for instructions on using `psypwdm`:

 - [Using the local password manager](https://nbviewer.org/github/KshkB/local-password-manager/blob/main/tutorials/using_pwdm.ipynb)

