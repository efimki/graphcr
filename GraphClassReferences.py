#!/usr/bin/python

import sys
sys.path.append("~/dot/codesearch-py")

import codesearch


class SymbolDefinition:
  skipped = set()
  processed = set()

  def __init__(self, signature, display_name):
    self.signature = signature
    self.display_name = display_name
    self.references = dict()

  def FindReferences(self, cs):
    print "Finding references of " + self.display_name
    if self.display_name in SymbolDefinition.processed:
      return
    #SymbolDefinition.processed.add(self.display_name)
    node = codesearch.XrefNode.FromSignature(cs, self.signature)
    edges = node.GetEdges(codesearch.EdgeEnumKind.DECLARES)
    for edge in edges:
      try:
        definitions = edge.GetRelatedDefinitions()
        for do in definitions:
          definition = do.GetEdges(codesearch.EdgeEnumKind.HAS_DEFINITION)
          if definition[0].GetXrefKind() != codesearch.NodeEnumKind.CLASS:
            continue
          try:
            name = definition[0].GetDisplayName()
            if name == self.display_name:
              continue
            if name in self.references:
              continue
            if name in SymbolDefinition.skipped:
              continue
            definition = do.GetEdges(codesearch.EdgeEnumKind.HAS_DEFINITION)
            if definition[0].GetXrefKind() != codesearch.NodeEnumKind.CLASS:
              print "- skipping " + name + " " + str(
                  definition[0].GetXrefKind())
              SymbolDefinition.skipped.add(name)
              continue
            print "+ adding " + name
            self.references[name] = SymbolDefinition(do.GetSignature(), name)
          except Exception as err1:
            print "Definition Exception: " + str(err1)
            continue
      except Exception as err:
        print "Edge Exception: " + str(err)
        continue

  def PrintReferences(self):
    for reference in self.references.keys():
      print self.display_name + " -> " + reference
    for reference in self.references.values():
      reference.PrintReferences()

  def PrintDigraph(self):
    print "digraph {"
    self.PrintReferences()
    print "}"

  def ResolveReferences(self, cs, level):
    if level <= 0:
      return
    self.FindReferences(cs)
    for reference in self.references.values():
      reference.ResolveReferences(cs, level - 1)


# The plugin needs to locate a local Chromium checkout. We are passing '.' as a
# path inside the source directory, which works if the current directory is
# inside the Chromium checkout. The configuration mechanism is likely to change.
cs = codesearch.CodeSearch(a_path_inside_source_dir="../chrome/android/src")

sig = cs.GetSignatureForSymbol("../chrome/android/src/net/http/http_network_transaction.cc", \
          "HttpNetworkTransaction")
#node = codesearch.XrefNode.FromSignature(cs, sig)
#print node

network_transaction = SymbolDefinition(sig, "HttpNetworkTransaction")
network_transaction.FindReferences(cs)
network_transaction.ResolveReferences(cs, 2)
network_transaction.PrintDigraph()
sys.exit(0)
