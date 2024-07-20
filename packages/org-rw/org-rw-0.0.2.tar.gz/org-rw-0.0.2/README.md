# Org-rw

A python library to parse, modify and save Org-mode files.

# Goals

-   Reading org-mode files, with all the relevant information (format,
    dates, lists, links, metadata, ...).
-   Modify these data and write it back to disk.
-   Keep the original structure intact (indentation, spaces, format,
    ...).

## Safety mechanism

As this library is still in early development. Running it over files
might produce unexpected changes on them. For this reason it\'s heavily
recommended to have backup copies before using it on important files.

By default the library checks that the re-serialization of the loaded
files will not produce any change, and throw an error in case it does.
But this cannot guarantee that later changes to the document will not
corrupt the output so be careful.

Also, see [Known issues:Structure
modifications](id:76e77f7f-c9e0-4c83-ad2f-39a5a8894a83) for cases when
the structure is not properly stored and can trigger this safety
mechanism on a false-positive.

# Known issues

## Structure modifications {#structure-modifications id="76e77f7f-c9e0-4c83-ad2f-39a5a8894a83"}

-   The exact format is not retained when saving dates/times. This might
    cause problems with the safety mechanism if you have dates that.
    Note that in both cases, doing `C-c C-c` on the date (from Emacs)
    will change it to the format that Org-rw serializes it to.
    -   Use multiple dashes for hour ranges, like
        `<2020-12-01 10:00----11:00>`{.verbatim}. It will get
        re-serialized as `<2020-12-01 10:00-11:00>`{.verbatim}, thus
        triggering the safety mechanism as unexpected changes have
        happened.
    -   Same in case hours are not two digits (with leading 0\'s if
        needed), like `<2020-12-01 9:00>`{.verbatim}. It will get
        serialized as `<2020-12-01 9:00>`{.verbatim}.

# Other python libraries for org-mode

[orgparse](https://github.com/karlicoss/orgparse)
:   More mature, but does not provide format support or writing back to
    disk.
