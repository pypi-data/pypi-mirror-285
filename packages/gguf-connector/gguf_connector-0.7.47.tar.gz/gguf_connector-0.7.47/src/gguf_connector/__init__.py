# !/usr/bin/env python3

__version__="0.7.47"

def __init__():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    subparsers.add_parser('cpp', help='[cpp] connector cpp')
    subparsers.add_parser('gpp', help='[gpp] connector gpp')
    subparsers.add_parser('g', help='[g] cli connector g')
    subparsers.add_parser('c', help='[c] gui connector c')
    subparsers.add_parser('m', help='[m] menu')
    subparsers.add_parser('i', help='[i] i/o web mirror')
    subparsers.add_parser('w', help='[w] page/container')
    subparsers.add_parser('r', help='[r] metadata reader')
    subparsers.add_parser('r2', help='[r2] metadata reader (beta)')
    subparsers.add_parser('pp', help='[pp] pdf analyzor pp')
    subparsers.add_parser('cp', help='[cp] pdf analyzor cp')
    subparsers.add_parser('ps', help='[ps] wav recognizor ps')
    subparsers.add_parser('cs', help='[cs] wav recognizor cs')
    subparsers.add_parser('cg', help='[cg] wav recognizor cg (online)')
    subparsers.add_parser('pg', help='[pg] wav recognizor pg (online)')
    args = parser.parse_args()

    if args.subcommand == 'm':
        from gguf_connector import m
    elif args.subcommand=="r":
        from gguf_connector import r
    elif args.subcommand=="r2":
        from gguf_connector import r2
    elif args.subcommand=="i":
        from gguf_connector import i
    elif args.subcommand=="w":
        from gguf_connector import w
    elif args.subcommand=="cg":
        from gguf_connector import cg
    elif args.subcommand=="pg":
        from gguf_connector import pg
    elif args.subcommand=="cs":
        from gguf_connector import cs
    elif args.subcommand=="ps":
        from gguf_connector import ps
    elif args.subcommand=="cp":
        from gguf_connector import cp
    elif args.subcommand=="pp":
        from gguf_connector import pp
    elif args.subcommand=="c":
        from gguf_connector import c
    elif args.subcommand=="cpp":
        from gguf_connector import cpp
    elif args.subcommand=="g":
        from gguf_connector import g
    elif args.subcommand=="gpp":
        from gguf_connector import gpp