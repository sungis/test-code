from collections import deque

class RadixTree:
    def __init__(self):
        """
        Create a Radix Tree with only the default node root.
        """
        self.root = RadixTreeNode()
        self.root.key = ""
        self.size = 0
            
    def insert(self, key, value, node=None):
        """
        Recursively insert the key in the radix tree
        """
        if not node:
            node = self.root
            self.size += 1

        number_of_matching_chars = node.get_number_of_matching_characters(key)

        # we are either at the root node
        # or we need to go down the tree
        if node.key == "" or number_of_matching_chars == 0 or (
        number_of_matching_chars < len(key) and number_of_matching_chars >= len(node.key)):
            flag = False
            new_text = key[number_of_matching_chars:]
            for child in node.children:
                if child.key.startswith(new_text[0]):
                    flag = True
                    self.insert(new_text, value, child)
                    break

            # just add the node as the child of the current node
            if not flag:
                n = RadixTreeNode()
                n.key = new_text
                n.real = True
                n.value = value

                node.children.append(n)

        # there is an exact match, just make the current node a data node
        elif number_of_matching_chars == len(key) and number_of_matching_chars == len(node.key):
            if node.real:
                raise DuplicateKeyError("Duplicate Key: '%s' for value: '%s' " % (key, node.value))

            node.real = True
            node.value = value

        # this node needs to be split as the key to be inserted
        # is a prefix of the current node key
        elif number_of_matching_chars > 0 and number_of_matching_chars < len(node.key):
            n1 = RadixTreeNode()
            n1.key = node.key[number_of_matching_chars:]
            n1.real = node.real
            n1.value = node.value
            n1.children = node.children

            node.key = key[0:number_of_matching_chars]
            node.real = False
            node.children = [n1]

            if number_of_matching_chars < len(key):
                n2 = RadixTreeNode()
                n2.key = key[number_of_matching_chars:]
                n2.real = True
                n2.value = value
                node.children.append(n2)
            else:
                node.value = value
                node.real = True

        # this key needs to be added as the child of the current node
        else:
            n = RadixTreeNode()
            n.key = node.key[number_of_matching_chars:]
            n.children = node.children
            n.real = node.real
            n.value = node.value

            node.key = key
            node.real = True
            node.value = value
            node.children.append(n)

    def delete(self, key):
        """
        Deletes the key from the trie
        """
        visitor = VisitorDelete()

        self.visit(key, visitor)

        if (visitor.result):
            self.size -= 1

        return visitor.result

    def find(self, key):
        """
        Returns the value for the given key
        """
        visitor = VisitorFind()

        self.visit(key, visitor)

        return visitor.result

    def complete(self, key, node=None, base=""):
        """
        Complete the a prefix to the point where ambiguity starts.

        Example:
        If a tree contain "blah1", "blah2"
        complete("b") -> return "blah"

        Returns the unambiguous completion of the string
        """
        if not node:
            node = self.root

        i = 0
        key_len = len(key)
        node_len = len(node.key)

        while i < key_len and i < node_len:
            if key[i] != node.key[i]:
                break

            i += 1

        if i == key_len and i <= node_len:
            return base + node.key

        elif node_len == 0 or (i < key_len and i >= node_len):
            beginning = key[0:i]
            ending = key[i:key_len]
            for child in node.children:
                if child.key.startswith(ending[0]):
                    return self.complete(ending, child, base + beginning)

        return ""

    def search_prefix(self, key, record_limit):
        """
        Returns all keys for the given prefix
        """
        keys = []

        node = self._search_prefix(key, self.root)

        if node:
            if node.real:
                keys.append(node.value)
            self.get_nodes(node, keys, record_limit)

        return keys
    def high_light(self,content):
        buff = ''
        index = 0
        c_len=len(content)
        while (index < c_len):
          key = content[index]
          matches = self.search_prefix(key,100)
          flag = False
          for m in matches:
            if (index + len(m) > c_len):
              continue
            matchsource=content[index:index+len(m)]
            if(matchsource.lower() == m):
              buff += '<b>' + matchsource + '<b>'
              index +=len(m)
              flag = True
              break
          if flag :
            continue
          buff += key
          index +=1
        return buff

    def _search_prefix(self, key, node):
        """
        Util for the search_prefix function
        """
        result = None

        number_of_matching_chars = node.get_number_of_matching_characters(key)

        if number_of_matching_chars == len(key) and number_of_matching_chars <= len(node.key):
            result = node

        elif node.key == "" or (number_of_matching_chars < len(key) and number_of_matching_chars >= len(node.key)):
            new_text = key[number_of_matching_chars:]
            for child in node.children:
                if child.key.startswith(new_text[0]):
                    result = self._search_prefix(new_text, child)
                    break

        return result

    def get_nodes(self, parent, keys, limit):
        """
        Updates keys... (not really sure)
        """
        queue = deque(parent.children)

        while len(queue) != 0:
            node = queue.popleft()
            if node.real:
                keys.append(node.value)

            if len(keys) == limit:
                break

            queue.extend(node.children)


    def visit(self, prefix, visitor, parent=None, node=None):
        """
        Recursively visit the tree based on the supplied "key". Calls the Visitor
        for the node those key matches the given prefix
        """
        if not node:
            node = self.root

        number_of_matching_chars = node.get_number_of_matching_characters(prefix)

        # if the node key and prefix match, we found a match!
        if number_of_matching_chars == len(prefix) and number_of_matching_chars == len(node.key):
            visitor.visit(prefix, parent, node)

        # we are either at the root OR we need to traverse the children
        elif node.key == "" or (number_of_matching_chars < len(prefix) and number_of_matching_chars >= len(node.key)):
            new_text = prefix[number_of_matching_chars:]
            for child in node.children:
                # recursively search the child nodes
                if child.key.startswith(new_text[0]):
                    self.visit(new_text, visitor, node, child)
                    break


    def contains(self, key):
        """
        Returns True if the key is valid. False, otherwise.
        """
        visitor = VisitorContains()
        self.visit(key, visitor)
        return visitor.result

    def debug(self):
        """
        Returns a string representation of the radix tree.

        WARNING: Do not use on large trees!
        """

        lst = []
        self._debug_node(lst, 0, self.root)
        return "\r".join(lst)

    def _debug_node(self, lst, level, node):
        """
        Recursive utility method to generate visual tree

        WARNING: Do not use on large trees!
        """

        temp = " " * level
        temp += "|"
        temp += "-" * level

        if node.real:
            temp += "%s[%s]" % (node.key, node.value)
        else:
            temp += "%s" % (node.key)

        lst.append(temp)

        for child in node.children:
            self._debug_node(lst, level + 1, child)


class RadixTreeNode(object):
    def __init__(self):
        self.key = ""
        self.children = []
        self.real = False
        self.value = None

    def get_number_of_matching_characters(self, key):
        number_of_matching_chars = 0

        while number_of_matching_chars < len(key) and number_of_matching_chars < len(self.key):
            if key[number_of_matching_chars] != self.key[number_of_matching_chars]:
                break
            number_of_matching_chars += 1

        return number_of_matching_chars


class Visitor(object):
    def __init__(self, initial_value=None):
        self.result = initial_value

    def visit(self, key, parent, node):
        pass


class VisitorFind(Visitor):
    def visit(self, key, parent, node):
        if node.real:
            self.result = node.value


class VisitorContains(Visitor):
    def visit(self, key, parent, node):
        self.result = node.real


class VisitorDelete(Visitor):
    def visit(self, key, parent, node):
        self.result = node.real

        # if it is a real node
        if self.result:
            # If there are no node children we need to
            # delete it from its parent's children list
            if len(node.children) == 0:
                for child in parent.children:
                    if child.key == node.key:
                        parent.children.remove(child)
                        break

                # if the parent is not a real node and there
                # is only one child then they need to be merged
                if len(parent.children) == 1 and not parent.real:
                    self.merge_nodes(parent, parent.children[0])

            # we need to merge the only child of this node with itself
            elif len(node.children) == 1:
                self.merge_nodes(node, node.children[0])

            # we just need to mark the node as non-real
            else:
                node.real = False

    def merge_nodes(self, parent, child):
        """
        Merge a child into its parent node. The operation is only valid if it is
        the only child of the parent node and parent node is not a real node.
        """
        parent.key += child.key
        parent.real = child.real
        parent.value = child.value
        parent.children = child.children


class DuplicateKeyError(Exception):
    pass


if __name__ == "__main__":
    rt = RadixTree()

    rt.insert("apple", "apple")
    rt.insert("appleshack", "appleshack")
    rt.insert("appleshackcream", "appleshackcream")
    rt.insert("applepie", "applepie")
    rt.insert("ape", "ape")

    content = "apple ape applepie hhj"

    rt.high_light(content)

    buff = ''
    index = 0
    c_len=len(content)
    while (index < c_len):
      key = content[index]
      matches = rt.search_prefix(key,100)
      flag = False
      for m in matches:
        if (index + len(m) > c_len):
          continue
        matchsource=content[index:index+len(m)]
        if(matchsource.lower() == m):
          buff += '<b>' + matchsource + '<b>'
          index +=len(m)
          flag = True
          break
      if flag :
        continue
      buff += key
      index +=1

    print buff



    print(rt.debug())
