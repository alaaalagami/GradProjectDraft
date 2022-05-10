from em_search import EM_Searcher
searcher = EM_Searcher()
solutions = searcher.validate()
print('------------------Solutions----------------\n')
for sol in solutions:
    print(sol, '\n')
searcher.visulaize_solutions()