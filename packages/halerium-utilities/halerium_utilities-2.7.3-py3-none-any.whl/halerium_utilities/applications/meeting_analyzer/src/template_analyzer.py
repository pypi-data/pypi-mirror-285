import logging

from halerium_utilities.board import Board, BoardNavigator
from halerium_utilities.prompt.agents import call_agent


# setup logging with debug level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def execute_botcard(board: Board, card_id: str):
    gen = call_agent(board.to_dict(), card_id, parse_data=True)
    result = ""
    for data in gen:
        if data.event == "chunk":
            result += data.data["chunk"]

    board.update_card({'id': card_id, 'type_specific': {'prompt_output': result}})
    return result


def analyze_snippet(board_path: str):
    board = Board.from_json(board_path)
    navigator = BoardNavigator(board)
    execution_order = navigator.get_execution_order(
        navigator.cards, keep_only_executable=True)

    ids_and_answers = {}
    for card_id in execution_order:
        if is_execute_and_show(navigator, card_id):  # card in a red frame
            answer = execute_botcard(board, card_id)
            logging.info(f"Saving board {board_path}.")
            board.to_json(board_path)
            ids_and_answers[card_id] = answer
        elif is_execute_only(navigator, card_id):  # card in a yellow frame
            execute_botcard(board, card_id)
            logging.info(f"Saving board {board_path}.")
            board.to_json(board_path)
        else:
            pass

    logging.info(f"Saving board {board_path}.")
    board.to_json(board_path)
    return ids_and_answers


def is_in_colored_frame(navigator, card_id, color_name):
    containing_frames = navigator.get_containing_frame_ids(card_id)
    for frame_id in containing_frames:
        frame_color = getattr(navigator.cards[frame_id].type_specific, "color", None)
        if frame_color == color_name:
            return True

    return False


COLORS = {
    "yellow": "note-color-8",  # is_execute_and_show
    "blue": "note-color-4",  # is_execute_only
    "red": "note-color-6",  # don't care
}


def is_execute_and_show(navigator, card_id):
    return is_in_colored_frame(navigator, card_id, COLORS["yellow"])


def is_execute_only(navigator, card_id):
    return is_in_colored_frame(navigator, card_id, COLORS["blue"])
