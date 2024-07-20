#import "@preview/wrap-it:0.1.0": wrap-content  // https://github.com/ntjess/wrap-it/blob/main/docs/manual.pdf
#import "./doc_templates/src/note.typ": *
#import "./doc_templates/src/style.typ": set_style


#show: doc => set_style(
    topic: "kfsmedia",
    author: "구FS",
    language: "EN",
    doc
)
#set text(size: 3.5mm)


#align(center, text(size: 2em, weight: "bold")[kfsmedia])
#line(length: 100%, stroke: 0.3mm)
\
\
= Introduction

This library is a collection of miscellaneouns media functions that turned out to be quite useful to have while creating my other projects.

For further documentation, read the provided docstrings or feel free to send me a message. I'm also always happy about sugggestions and tips.

= Table of Contents

#outline()

#pagebreak(weak: true)

= Installation
== PyPI

+ `pip install kfsmedia`