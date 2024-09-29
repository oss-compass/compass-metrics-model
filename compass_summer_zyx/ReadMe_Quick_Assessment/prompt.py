'''
Descripttion: 包含函数prompt
version: V1.0
Author: zyx
Date: 2024-09-20 10:06:56
LastEditors: zyx
LastEditTime: 2024-09-28 07:40:16
'''
# '''Next, I will give you a README document for you to rate from a completeness perspective, each score is 100 points, the weight ratio between the scores is 3:3:3:1, and the score should mainly include the following:
# Project Overview: The README should clearly explain what the project does, including the goals of the project, and the problem the project is trying to solve.
#     - Installation guide: The README should contain all the necessary steps on how to install and configure the project. There should also be a clear list and installation instructions for the required dependencies.
#     - Communication information: If a user, developer, or contributor needs to contact a project maintainer, the README should provide the required contact information or link.
#     - Other information: whether the paper has been included, whether it has been cited, and whether there are any common problems that need to be troubled.
# Please give the results for each of the four ratings for the README document you obtained,wonderful documents are excellent documents with a score of at least 85 points,Ordinary documents are excellent documents with a score of no higher than 50 points, and give the results as {Project Overview: XX, Installation Guide: xx, Communication Information: xx, Other Information: XX, Overall Rating: xx} to give the results'''
# #             prompt = """

# The first step is to compare the documents, I will give you a comparison between an excellent document and a non-excellent document in turn, the score of the non-excellent bin is not more than 60, and the score of the excellent document is less than 90. Please do a detailed comparison of the four indicators of project overview, installation guide, communication information, and other information, the following is the training document, and the beginning of each document represents its label, such as wonderful: is an excellent ReadME document, and ordinary is a non-excellent ReadME document. Please rate them in turn

# """
def prompt_case(case):
    """
    prompt engineering
    :param case: 选择completeness1，definition1
    :return: prompt
    """
    prompt = ""
    try:
        if case == "completeness1":

            prompt ="""
                If you are an open source project ReadMe document evaluator, ReadMe documents mainly include Chinese and English two languages, next I will first give you 15 ReadMe documents 
                with good ratings and 15 ReadMe documents with bad ratings, please learn to evaluate the integrity of these documents through comparative learning, the completeness is mainly 
                from the project overview, installation guide, communication information, and other information aspects of the four indicators to evaluate the excellence of the documents, The 
                full score of each indicator is 100, and the scores are summarized according to the results, and the scoring results are required to retain two decimal places, and the weight 
                of the four indicators is 3:3:3:1. The four indicators are described in detail as follows:

                    - Project Overview: The README should clearly explain what the project does, including the goals of the project, and the problems the project is trying to solve.
                    - Installation Guide: The README should include all the necessary steps on how to install and configure the project. There should also be a clear list and installation 
                    instructions for the required dependencies.
                    - Communication information: If a user, developer, or contributor needs to contact a project maintainer, the README should provide the required contact information or link.
                    - Other information: whether the paper is included, whether it is cited, and whether there are common problems to troubleshoot.
                
                Next, I will use the new ReadME documents in addition to the above 30 documents, please use the four metric characteristics you have learned, and compare them with the 30 ReadME
                documents I gave you before, and the comprehensive score is the sum of the weights of the four indicators, and the Comprehensive Score is the sum of the weights of the scores of
                the four indicators, so please calculate it in detail,and finally give the scoring results in the form of markdown: {Project Overview: XX, Installation Guide: xx, Communication 
                Information: xx, Other Information: XX, Comprehensive Score: xx}. The first step is to conduct a comparative study of the documents, through the learning comparison between 15
                excellent documents and 15 non-excellent documents,please conduct a detailed comparative study of the four indicators of project overview, installation guide, communication 
                information, and other information, the following is the training document, the beginning of each document all represent its tags, e.g. wonderful: is a ReadME excellent document,
                  and ordinary is a non-excellent ReadME document.

            """
            
        elif case == "completeness2":

            
            prompt = """  The first step is to conduct a comparative study of the documents, through the learning comparison between 15 excellent documents and 15 non-excellent documents,
                        please conduct a detailed comparative study of the four indicators of project overview, installation guide, communication information, and other information, the following is
                        the training document, the beginning of each document all represent its tags, e.g. wonderful: is a ReadME excellent document, and ordinary is a non-excellent ReadME document.
                        Because of the token limit, I will pass it to you in batches. Finally,please give the results of the current completeness score, in markdown form:
                        {Project Overview: XX, Installation Guide: xx, Communication Information: xx, Other information: XX, comprehensive score: xx} gives the scoring results,
                        and at the same time gives the scoring basis.
                        Example：
                questions: "
                            The Moby Project
                            ================

                            ![Moby Project logo](docs/static_files/moby-project-logo.png "The Moby Project")

                            Moby is an open-source project created by Docker to enable and accelerate software containerization.

                            It provides a "Lego set" of toolkit components, the framework for assembling them into custom container-based systems, and a place for all container enthusiasts and professionals to experiment and exchange ideas.
                            Components include container build tools, a container registry, orchestration tools, a runtime and more, and these can be used as building blocks in conjunction with other tools and projects.

                            ## Principles

                            Moby is an open project guided by strong principles, aiming to be modular, flexible and without too strong an opinion on user experience.
                            It is open to the community to help set it
                            It is your responsibility to ensure that your use and/or transfer does not
                            violate applicable laws.

                            For more information, please see https://www.bis.doc.gov

                            Licensing
                            =========
                            Moby is licensed under the Apache License, Version 2.0. See
                            [LICENSE](https://github.com/moby/moby/blob/master/LICENSE) for the full
                            license text.
                
                            "
                return: {Project Overview: 50, Installation Guide: 0, Communication Information: 40, Other Information: 0, Comprehensive Score: 50*0.3+0*0.3+40*0.3+1*0.1=27}. 
                     """
            # When you receive "Proceed to the second step" it means that the training process has ended.
        
        elif case == "completeness3":

            prompt = """
                    After the above learning, you should have understood the specific basis for evaluating completeness among the 30 readme files, and then I will give you a Readme document,
                    please use the four integrity scoring criteria you have learned, and compare it with the previous 30 ReadME documents to you, give the document a score, and again remind
                    that the ratio between the four indicators is 3:3:3:1, and the full score for each item is 100 points, and please keep two decimal places for the scoring results.For the
                    four completeness indicators, the score of the project is 80-100 points for the near-excellent project, 60-80 points for the relatively close ones, 40-60 points for the 
                    less close, and 0-40 points for the worst items. The comprehensive score is the weight sum of the score, If this indicator is not available, it is scored on a scale of 0-40,
                    note: Please give a detailed score for each indicator, in the form of markdown: {Project Overview: XX, Installation Guide: xx, Communication Information: xx, 
                    Other Information: XX, Comprehensive Score: xx} to give the scoring results, and give the scoring basis.

                    """
            
        elif case == "definition1":

            prompt ="""
                    If you are an open source project markdown document evaluator, ReadMe documents mainly include Chinese and English two languages, next I will first give you 15 markdown documents 
                    with good ratings and 15 markdown documents with bad scores, please learn to evaluate the clarity part of these documents through comparative learning, clarity mainly from the 
                    document formatting effect, grammar and spelling errors scoring two indicators to evaluate the excellence of the document, Each indicator is scored out of 100, and the scores 
                    are summarized according to the results, and the scoring results are required to retain two decimal places, and the indicators of these two indicators are described in detail
                      as follows:

                        - Formatting of the document: Whether the document has a clear structure and layout, including headings, paragraphs, lists, code blocks, etc., so that readers can quickly
                          find the information they need.
                        - Grammar and spelling errors: Grammar and spelling errors are scored by a model-assisted check. Scores can be given directly by the model.

                    Next, I will use the new ReadME documents in addition to the above thirty, please use the two metric characteristics you have learned, and compare them with the previous thirty 
                    ReadME documents,and comprehensively score them as the sum of the weights of the two indicators, and finally give the scoring results in the form of a dictionary: {Document 
                    Formatting Effect Score: XX, Grammar and Spelling Error Score: xx}. The steps to achieve this are as follows:
                    
                """
            
        elif case == "definition2":

            prompt = """  The first step is to conduct a comparative study of the documents, through the learning comparison between 15 excellent documents and 15 non-excellent documents, 
                            please conduct a detailed comparative study of the four indicators of project overview, installation guide, communication information, and other information, 
                            the following is the training document, the beginning of each documentall represent its tags, e.g. wonderful: is a ReadME excellent document, and ordinary is 
                            a non-excellent ReadME document. Because of the token limit, I will pass it to you in batches. When you enter the second step, the training process has ended."""
        
        elif case == "definition3":

            prompt = """
                       The second step is the grading process of the document, after the above learning, you should have understood the specific basis for the evaluation between the 30 Readme 
                       documents, and then I will give you a Readme document, please use what you have learned, and at the same time compare it with the 30 ReadME documents that were previously
                         given to you, and score the given documents, each with a full score of 100 points, and the scoring result should be kept to two decimal places. For the two clarity metrics 
                         of attention, the Document formatting effect is 80-100 for the project with a near-good score, 60-80 for the relatively close item, 40-60 for the less close, and the worst 
                         item on a scale of 0-40. Grammar and spelling errors: Scored based on the number and consistency of errors. The composite score is the sum of the weights of the scores, 
                         note: Please give the detailed scores of each indicator in the form of markdown::{Document formatting effect: XX, grammar and spelling errors: XX}, and give the basis for 
                         the score.                    
                    """
        else:
            raise ValueError(f"case {case} error,unexisting")     
        
        return prompt
    except:
        raise ValueError(f"case {case} error,unexisting")            
