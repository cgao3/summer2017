import numpy as np
from commons.definitions import INPUT_DEPTH, INPUT_WIDTH, BuildInputTensor, BOARD_SIZE, MoveConvertUtil


class PositionActionDataReader(object):
    '''
    input depth = INPUT_DEPTH,
    see commons.definitions

    Input raw data format:
    each line contains a sequence of moves, representing a state-action pair,
    the last move is an action for prediction.
    e.g.,
    B[b3] W[c6] B[d6] W[c7] B[f5] W[d8] B[f7] W[f6]
    f6 is action, moves before that represents a board state.

    This reader reads a batch from raw-input-data, then prepares a batch of tensor inputs for neural net
    '''
    def __init__(self, position_action_filename, batch_size):

        self.data_file_name = position_action_filename
        self.batch_size = batch_size
        self.reader = open(self.data_file_name, "r")
        self.batch_positions = np.ndarray(shape=(batch_size, INPUT_WIDTH, INPUT_WIDTH, INPUT_DEPTH), dtype=np.uint32)
        self.batch_labels = np.ndarray(shape=(batch_size,), dtype=np.uint16)
        self.currentLine = 0

        '''whether or not random 180 flip when preparing a batch '''
        self.enableRandomFlip=False

        '''see BuildInputTensor in commons.definitions for the detailed format of input data'''
        self.tensorMakeUtil=BuildInputTensor()

    def close_file(self):
        self.reader.close()

    def prepare_next_batch(self):
        self.batch_positions.fill(0)
        self.batch_labels.fill(0)
        next_epoch = False
        for i in range(self.batch_size):
            line = self.reader.readline()
            line = line.strip()
            if len(line) == 0:
                self.currentLine = 0
                self.reader.seek(0)
                line = self.reader.readline()
                next_epoch = True
            self._build_batch_at(i, line)
            self.currentLine += 1
        return next_epoch

    def _build_batch_at(self, kth, line):
        arr = line.strip().split()
        intMove = self._toIntMove(arr[-1])
        rawMoves=arr[0:-1]
        intgamestate=[self._toIntMove(i) for i in rawMoves]
        if self.enableRandomFlip and np.random.random()<0.5:
            intMove=MoveConvertUtil.rotateMove180(intMove)
            for i in range(len(intgamestate)):
                intgamestate[i]=MoveConvertUtil.rotateMove180(intgamestate[i])
        self.tensorMakeUtil.makeTensorInBatch(self.batch_positions, self.batch_labels, kth, intgamestate, intMove)

    def _toIntMove(self, raw):
        x = ord(raw[2].lower()) - ord('a')
        y = int(raw[3:-1]) - 1
        assert(0<=x<BOARD_SIZE and 0<=y<BOARD_SIZE)
        imove=x*BOARD_SIZE+y
        return imove


if __name__ == "__main__":
    print("Test input_data_util.PositionActionDataReader")
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default="")
    parser.add_argument('--batch_size', type=int, default=100)
    args=parser.parse_args()
    if not args.input_file:
        print("please indicate --input_file")
        exit(0)
    reader=PositionActionDataReader(args.input_file, args.batch_size)
    print("current line ", reader.currentLine)
    reader.prepare_next_batch()
    print("current line ", reader.currentLine)