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
	      print "- skipping " + name + " " + str(definition[0].GetXrefKind())
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
cs = codesearch.CodeSearch(a_path_inside_source_dir='../chrome/android/src')

sig = cs.GetSignatureForSymbol('../chrome/android/src/net/http/http_network_transaction.cc', \
          'HttpNetworkTransaction')
#node = codesearch.XrefNode.FromSignature(cs, sig)
#print node

#network_transaction = SymbolDefinition(sig, 'HttpNetworkTransaction');
#network_transaction.FindReferences(cs)
#network_transaction.ResolveReferences(cs,2)
#network_transaction.PrintDigraph()
#sys.exit(0)

def GetFileForClass(cs, class_name):
  response = cs.SendRequestToServer(codesearch.CompoundRequest(
    search_request=[
        codesearch.SearchRequest(query='class:' + class_name)
    ]))

  assert isinstance(response, codesearch.CompoundResponse)
  assert hasattr(response, 'search_response')
  assert isinstance(response.search_response, list)
  assert isinstance(response.search_response[0], codesearch.SearchResponse)
  return response.search_response[0].search_result[0].top_file.file.name

file_prefix = '../chrome/android/'

def GetSignatureForClass(cs, class_name):
  file_name = GetFileForClass(cs, class_name)
  sig = cs.GetSignatureForSymbol(file_prefix + file_name, class_name)
  return sig

print GetSignatureForClass(cs, "HttpNetworkTransaction")
print GetSignatureForClass(cs, "net::UrlRequestContext")
print GetSignatureForClass(cs, "CronetEngine")
print GetSignatureForClass(cs, "CronetEngine.Builder")
sys.exit(0)

# The backend takes a CompoundRequest object ...
response = cs.SendRequestToServer(codesearch.CompoundRequest(
    search_request=[
        codesearch.SearchRequest(query='class:CronetEngine')
    ]))

# ... and returns a CompoundResponse
assert isinstance(response, codesearch.CompoundResponse)

# Both CompoundRequest and CompoundResponse are explained in
# codesearch/messages.py. Since our request was a |search_request| which is a
# list of SearchRequest objects, our CompoundResponse object is going to have a
# |search_response| field ...

assert hasattr(response, 'search_response')

# containing a list of SearchResponse objects ...

assert isinstance(response.search_response, list)
assert isinstance(response.search_response[0], codesearch.SearchResponse)

# We can now examine the contents of the SearchResponse object to see what the
# server sent us. The fields are explained in message.py.

for search_result in response.search_response[0].search_result:
    print search_result
    assert isinstance(search_result, codesearch.SearchResult)
    print search_result.top_file.file.name
    
#    definition = search_result.GetEdges(codesearch.EdgeEnumKind.HAS_DEFINITION)
#    print "***********" + str(definition)

    if not hasattr(search_result, 'snippet'):
	print "no snippet"
        continue

    for snippet in search_result.snippet:
        assert isinstance(snippet, codesearch.Snippet)

    # Just print the text of the search result snippet.
        print snippet.text.text

#	if definition[0].GetXrefKind() != codesearch.NodeEnumKind.CLASS:#
#	      print "- skipping " + name + " " + str(definition[0].GetXrefKind())
#              SymbolDefinition.skipped.add(name)
#              continue


sys.exit(0)

edges = node.GetEdges(codesearch.EdgeEnumKind.DECLARES)
#edges = node.GetEdges(codesearch.EdgeEnumKind.EXTENDS)

for edge in edges:
    #print edge
    print "***line:***" + edge.single_match.line_text
    #print "***sig:***" + edge.single_match.signature
    #declared_by = edge.GetEdges(codesearch.EdgeEnumKind.DECLARED_BY)
    #for db in declared_by:
    #  print "***declared_by:***" + db.single_match.line_text
    #definition_of = edge.GetEdges(codesearch.EdgeEnumKind.HAS_TYPE)
    try:
	    definition_of = edge.GetRelatedDefinitions()
	    for do in definition_of:
		try:
			print "***Related Definition of:***" + str(do)
	      		print "***Related Definition Name:***" + do.GetDisplayName()
		except:
			continue
	      
    except:
      continue 

#edges = node.GetEdges(codesearch.EdgeEnumKind.DECLARED_BY)
#for edge in edges:
#    print edge

print node.GetDisplayName()


