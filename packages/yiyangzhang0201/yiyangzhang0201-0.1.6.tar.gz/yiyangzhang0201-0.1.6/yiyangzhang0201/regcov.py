def stata_result_latex(code_list, fe_list, title):

    def find_first_i_prefix(items):
        for index, item in enumerate(items):
            if item.startswith('i.'):
                return index  # Return the index of the first match
        return -1

    # Get the current IPython session
    ipython = get_ipython()

    if len(code_list) == 1:
        ipython.run_cell_magic('stata', '', code)

        if len(fe_list) == 0:
            for code in code_list:
                output_convert = f"""
                outreg2 using results.tex, replace tex title("{title}") label
                """
                ipython.run_cell_magic('stata', '', output_convert)

        elif len(fe_list) > 0:
            for code in code_list:
                k = code.split()
                end = find_first_i_prefix(k)
                k = k[2: end]
                kv = ''
                for v in k:
                    kv += f'{v} '
                fe = ''
                for fe_n in fe_list[0]:
                    fe += f'{fe_n} FE, YES, '
                fe = fe[:-2]
                output_convert = f"""
                outreg2 using results.tex, replace tstat tex title("{title}") keep({kv}) addtext({fe})
                """
                ipython.run_cell_magic('stata', '', output_convert)

    elif len(code_list) > 1:
        for i in range(len(code_list)):
            if i == 0:
                ipython.run_cell_magic('stata', '', code_list[i])
                if len(fe_list[i]) == 0:
                    output_convert = f"""
            outreg2 using results.tex, replace tstat tex title("{title}") ctitle("Model 1") label
            """
                    ipython.run_cell_magic('stata', '', output_convert)
                else:
                    k = code_list[i].split()
                    end = find_first_i_prefix(k)
                    k = k[2: end]
                    kv = ''
                    for v in k:
                        kv += f'{v} '
                    fe = ''
                    for fe_n in fe_list[0]:
                        fe += f'{fe_n} FE, YES, '
                    fe = fe[:-2]
                    output_convert = f"""
                    outreg2 using results.tex, replace tstat tex title("{title}") ctitle("Model 1") keep({kv}) addtext({fe})
                    """
                    ipython.run_cell_magic('stata', '', output_convert)

            else:
                ipython.run_cell_magic('stata', '', code_list[i])
                if len(fe_list[i]) == 0:
                    output_convert = f"""
            outreg2 using results.tex, append ctitle("Model {i + 1}") label
            """
                    ipython.run_cell_magic('stata', '', output_convert)
                else:
                    k = code_list[i].split()
                    end = find_first_i_prefix(k)
                    k = k[2: end]
                    kv = ''
                    for v in k:
                        kv += f'{v} '
                    fe = ''
                    for fe_n in fe_list[i]:
                        fe += f'{fe_n} FE, YES, '
                    fe = fe[:-2]
                    output_convert = f"""
                    outreg2 using results.tex, append ctitle("Model {i + 1}") keep({kv}) addtext({fe}) tstat
                    """
                    ipython.run_cell_magic('stata', '', output_convert)