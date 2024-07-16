###############################################################################
#                                                                             #
#                      AUTOGENERATED TYPE STUB FILE                           #
#                                                                             #
#    This file was automatically generated. Do not modify it directly.        #
#    Any changes made here may be lost when the file is regenerated.          #
#                                                                             #
###############################################################################

class Document:

    def __init__(self, content, life=None):
        """Initialize self.  See help(type(self)) for accurate signature."""

    @property
    def content(self):
        ...

    @property
    def entity(self):
        ...

    @property
    def life(self):
        ...

class VectorisedGraph:

    def __init__(self):
        """Initialize self.  See help(type(self)) for accurate signature."""

    def append(self, nodes, edges):
        """
        Add all the documents from `nodes` and `edges` to the current selection

        Documents added by this call are assumed to have a score of 0.

        Args:
          nodes (list): a list of the node ids or nodes to add
          edges (list):  a list of the edge ids or edges to add

        Returns:
          A new vectorised graph containing the updated selection
        """

    def append_by_similarity(self, query, limit, window=None):
        """
        Add the top `limit` documents to the current selection using `query`

        Args:
          query (str or list): the text or the embedding to score against
          limit (int): the maximum number of new documents to add
          window ((int | str, int | str)): the window where documents need to belong to in order to be considered

        Returns:
          A new vectorised graph containing the updated selection
        """

    def append_edges(self, edges):
        """
        Add all the documents from `edges` to the current selection

        Documents added by this call are assumed to have a score of 0.

        Args:
          edges (list):  a list of the edge ids or edges to add

        Returns:
          A new vectorised graph containing the updated selection
        """

    def append_edges_by_similarity(self, query, limit, window=None):
        """
        Add the top `limit` edge documents to the current selection using `query`

        Args:
          query (str or list): the text or the embedding to score against
          limit (int): the maximum number of new documents to add
          window ((int | str, int | str)): the window where documents need to belong to in order to be considered

        Returns:
          A new vectorised graph containing the updated selection
        """

    def append_nodes(self, nodes):
        """
        Add all the documents from `nodes` to the current selection

        Documents added by this call are assumed to have a score of 0.

        Args:
          nodes (list): a list of the node ids or nodes to add

        Returns:
          A new vectorised graph containing the updated selection
        """

    def append_nodes_by_similarity(self, query, limit, window=None):
        """
        Add the top `limit` node documents to the current selection using `query`

        Args:
          query (str or list): the text or the embedding to score against
          limit (int): the maximum number of new documents to add
          window ((int | str, int | str)): the window where documents need to belong to in order to be considered

        Returns:
          A new vectorised graph containing the updated selection
        """

    def edges(self):
        """Return the edges present in the current selection"""

    def expand(self, hops, window=None):
        """
        Add all the documents `hops` hops away to the selection

        Two documents A and B are considered to be 1 hop away of each other if they are on the same
        entity or if they are on the same node/edge pair. Provided that, two nodes A and C are n
        hops away of  each other if there is a document B such that A is n - 1 hops away of B and B
        is 1 hop away of C.

        Args:
          hops (int): the number of hops to carry out the expansion
          window ((int | str, int | str)): the window where documents need to belong to in order to be considered

        Returns:
          A new vectorised graph containing the updated selection
        """

    def expand_by_similarity(self, query, limit, window=None):
        """
        Add the top `limit` adjacent documents with higher score for `query` to the selection

        The expansion algorithm is a loop with two steps on each iteration:
          1. All the documents 1 hop away of some of the documents included on the selection (and
        not already selected) are marked as candidates.
         2. Those candidates are added to the selection in descending order according to the
        similarity score obtained against the `query`.

        This loops goes on until the current selection reaches a total of `limit`  documents or
        until no more documents are available

        Args:
          query (str or list): the text or the embedding to score against
          window ((int | str, int | str)): the window where documents need to belong to in order to be considered

        Returns:
          A new vectorised graph containing the updated selection
        """

    def expand_edges_by_similarity(self, query, limit, window=None):
        """
        Add the top `limit` adjacent edge documents with higher score for `query` to the selection

        This function has the same behavior as expand_by_similarity but it only considers edges.

        Args:
          query (str or list): the text or the embedding to score against
          limit (int): the maximum number of new documents to add
          window ((int | str, int | str)): the window where documents need to belong to in order to be considered

        Returns:
          A new vectorised graph containing the updated selection
        """

    def expand_nodes_by_similarity(self, query, limit, window=None):
        """
        Add the top `limit` adjacent node documents with higher score for `query` to the selection

        This function has the same behavior as expand_by_similarity but it only considers nodes.

        Args:
          query (str or list): the text or the embedding to score against
          limit (int): the maximum number of new documents to add
          window ((int | str, int | str)): the window where documents need to belong to in order to be considered

        Returns:
          A new vectorised graph containing the updated selection
        """

    def get_documents(self):
        """Return the documents present in the current selection"""

    def get_documents_with_scores(self):
        """Return the documents alongside their scores present in the current selection"""

    def nodes(self):
        """Return the nodes present in the current selection"""

    def save_embeddings(self, file):
        """Save the embeddings present in this graph to `file` so they can be further used in a call to `vectorise`"""

def generate_property_list(entity, filter_out=..., force_static=...):
    ...
