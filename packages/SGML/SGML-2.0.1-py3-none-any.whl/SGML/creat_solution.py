def create_solution_function(expression, variables):
    def solution(feature):
        feature_dict = {var: feature[var] for var in variables}
        result = eval(expression, feature_dict)
        return result

    return solution




