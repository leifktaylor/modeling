def linear_search(item, input_list, add_if_empty=False):
    """
    Searches for item in list and returns index.
    If duplicate item exists, will return the index of the first item found.
    :param item: item searched for
    :param input_list: list to search
    :return: list index
    """
    for i in range(0, len(input_list)):
        if input_list[i] == item:
            return i
    if add_if_empty:
        input_list.append(item)
        return len(input_list) - 1
    else:
        return None


def binary_search_check(item, input_list, count=0):
    """
    Searches an ordered list using a binary search for the given item.
    Doesn't actually work - because in recursion it splits the list up each
    time and does not return the correct index with regards to the original list.

    Because of this, it will just return True or False.

    :param item: item to search for
    :param input_list: list to use
    :return: list index
    """
    count += 1
    if count >= 100:
        print('Item not found. Max attempts of {0} Reached'.format(count))
        return False
    mid = len(input_list)/2
    if input_list[mid] == item:
        return True
    elif input_list[mid] > item:
        return binary_search_check(item, input_list[:mid], count)
    elif input_list[mid] < item:
        return binary_search_check(item, input_list[mid:], count)



def binary_search(item, input_list, bottom, top, count=0):
    # TODO WIP
    """
    Searches an ORDERED list and bisects until item index is returned.

    :param item: item to search for.
    :param input_list: list object that is ordered.
    :return: returns index in list of item
    """
    mid = len(input_list)//2
    count += 1
    if count >= 100:
        print('Recursion limit reached.')
        return None
    # Base case
    if input_list[mid] == item:
        return mid
    elif input_list[mid] > item:
        return binary_search(item, input_list, bottom, top, count)
    elif input_list[mid] < item:
        return binary_search(item, input_list, bottom, top, count)
    pass