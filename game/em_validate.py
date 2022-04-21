from em_search import EM_Searcher
searcher = EM_Searcher()
solutions = searcher.validate()
print('------------------Solutions----------------')
for sol in solutions:
    print(sol)
searcher.visulaize_solutions()