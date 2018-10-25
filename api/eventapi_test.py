from eventregistry import *
er = EventRegistry(apiKey = "f5d1a933-18ca-48d4-b740-d32263df02f4")
# input string from search bar output into George Clooney
q = QueryArticlesIter(conceptUri = er.getConceptUri("George Clooney"))
for art in q.execQuery(er, sortBy = "date"):
    print art
# to access local host: python -m SimpleHTTPServer
