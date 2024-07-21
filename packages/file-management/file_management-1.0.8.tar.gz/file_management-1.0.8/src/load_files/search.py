import os
import logging

logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d",
    format="%(levelname)s - %(asctime)s - %(message)s")


class Search:
    """
    Search Stack
    ------------

    """

    def __init__(self):
        self.data = []

    def search(self, directory, file_ext):
        """
        Recursively reads all Python files from the given directory, passes them to the API for comment insertion,
        and writes the commented code back to the respective files.

        Provide the root (i.e. '.')

        Parameters
        ----------
            directory: provide the directory to search
            file_ext: provide the extension of the file you'd like to work with

        Returns
        -------
            file_path generator object

        Usage::
            >>> stack = Search()
            >>> stack.search('src', '.py')

        """

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(file_ext):
                    file_path = os.path.join(root, file)
                    self.data.append(file_path)

    def __iter__(self):
        """
        Initializes search method as an iterator.
        For provided directory root and file extension,
        returns a list of files.

        Usage::
            >>> stack = Search()
            >>> stack.search('tests', '.py')
            >>> iter_stack = iter(stack)
            >>> next(iter_stack)
            'tests/test_openai_client.py'
        """
        self._index = 0 # pylint disable=attribute-defined-outside-init
        return self # pylint disable=attribute-defined-outside-init

    def __next__(self): #pylint disable=inconsistent-return-statements
        """ 
        Returns the next file found in the iteration.

        Usage::
            >>> stack = Search()
            >>> stack.search('tests', '.py')
            >>> iter_stack = iter(stack)
            >>> next(iter_stack)
            'tests/test_openai_client.py'

        """
        try:
            if self._index < len(self.data):
                result = self.data[self._index]
                self._index += 1
                return result
        except StopIteration as err:
            # Once the list or object is complete, this raises stop iterable
            logging.info(f"Processing completed {err}")
        # return result


if __name__ == "__main__":
    Search()

    # Example usage
    # stack = Search()
    # stack.search('src', '.py')
    # print(stack.data)
