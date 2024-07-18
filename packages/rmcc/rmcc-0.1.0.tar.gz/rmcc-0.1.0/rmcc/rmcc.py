from dataclasses import dataclass

from .exception import InvalidElementError


@dataclass
class MeshCode:
    __primary_y: int  # lat
    __primary_x: int  # lon
    __secondary_y: int
    __secondary_y: int
    __secondary_x: int
    __tertiary_y: int
    __tertiary_x: int
    __quaternary_y: int
    __quaternary_x: int
    __dimension: int

    def __init__(
        self,
        primary_y,
        primary_x,
        secondary_y,
        secondary_x,
        tertiary_y,
        tertiary_x,
        quaternary,
    ):
        self.__primary_y = primary_y
        self.__primary_x = primary_x
        self.__secondary_y = secondary_y
        self.__secondary_x = secondary_x
        self.__tertiary_y = tertiary_y
        self.__tertiary_x = tertiary_x
        if quaternary < 0:
            self.__quaternary_y = -1
            self.__quaternary_x = -1
        else:
            b = format(quaternary - 1, "02b")
            self.__quaternary_y = int(b[0])
            self.__quaternary_x = int(b[1])

        if self.__primary_x < 0 or self.__primary_y < 0:
            raise InvalidElementError(
                "y=" + str(self.__primary_y) + ", x=" + str(self.__primary_x)
            )
        if self.__secondary_x < 0 or self.__secondary_y < 0:
            self.__dimension = 1
            return
        if self.__tertiary_x < 0 or self.__tertiary_y < 0:
            self.__dimension = 2
            return
        if self.__quaternary_x < 0 or self.__quaternary_y < 0:
            self.__dimension = 3
            return
        self.__dimension = 4
        return

    @staticmethod
    def parse(code):
        tmp = code.split("-")

        dimension: int = len(tmp)

        primary_y: int = int(tmp[0][0:2])
        primary_x: int = int(tmp[0][2:4])
        secondary_y: int = int(tmp[1][0]) if dimension >= 2 else -1
        secondary_x: int = int(tmp[1][1]) if dimension >= 2 else -1
        tertiary_y: int = int(tmp[2][0]) if dimension >= 3 else -1
        tertiary_x: int = int(tmp[2][1]) if dimension >= 3 else -1
        quaternary: int = int(tmp[3]) if dimension >= 4 else -1

        return MeshCode(
            primary_y,
            primary_x,
            secondary_y,
            secondary_x,
            tertiary_y,
            tertiary_x,
            quaternary,
        )

    def getDimension(self) -> int:
        return self.__dimension

    def getMeshCode(self) -> str:
        if self.__secondary_x < 0 or self.__secondary_y < 0:
            return "{}{}".format(self.__primary_y, self.__primary_x)
        if self.__tertiary_x < 0 or self.__tertiary_y < 0:
            return "{}{}-{}{}".format(
                self.__primary_y,
                self.__primary_x,
                self.__secondary_y,
                self.__secondary_x,
            )
        if self.__quaternary_x < 0 or self.__quaternary_y < 0:
            return "{}{}-{}{}-{}{}".format(
                self.__primary_y,
                self.__primary_x,
                self.__secondary_y,
                self.__secondary_x,
                self.__tertiary_y,
                self.__tertiary_x,
            )
        return "{}{}-{}{}-{}{}-{}".format(
            self.__primary_y,
            self.__primary_x,
            self.__secondary_y,
            self.__secondary_x,
            self.__tertiary_y,
            self.__tertiary_x,
            self.__quaternary_x + self.__quaternary_y * 2 + 1,
        )

    def shiftPrimary(self, dy, dx):
        self.__primary_y += dy
        self.__primary_x += dx

    def shiftSecondary(self, dy, dx):
        self.__secondary_y += dy
        self.__secondary_x += dx

        qy, ry = self.__secondary_y // 8, self.__secondary_y % 8
        qx, rx = self.__secondary_x // 8, self.__secondary_x % 8

        self.__secondary_y, self.__secondary_x = ry, rx
        if qy == 0 and qx == 0:
            return
        self.shiftPrimary(qy, qx)

    def shiftTertiary(self, dy, dx):
        self.__tertiary_y += dy
        self.__tertiary_x += dx

        qy, ry = self.__tertiary_y // 10, self.__tertiary_y % 10
        qx, rx = self.__tertiary_x // 10, self.__tertiary_x % 10

        self.__tertiary_y, self.__tertiary_x = ry, rx
        if qy == 0 and qx == 0:
            return
        self.shiftSecondary(qy, qx)

    def shiftQuaternary(self, dy, dx):
        self.__quaternary_y += dy
        self.__quaternary_x += dx

        qy, ry = self.__quaternary_y // 2, self.__quaternary_y % 2
        qx, rx = self.__quaternary_x // 2, self.__quaternary_x % 2

        self.__quaternary_y, self.__quaternary_x = ry, rx
        if qy == 0 and qx == 0:
            return
        self.shiftTertiary(qy, qx)

    def shift(self, dy, dx):
        if self.getDimension() == 4:
            self.shiftQuaternary(dy, dx)
            return
        if self.getDimension() == 3:
            self.shiftTertiary(dy, dx)
            return
        if self.getDimension() == 2:
            self.shiftSecondary(dy, dx)
            return
        self.shiftPrimary(dy, dx)
        return

    def calNeighbors(self, distance):
        coordinates: list = self.__calCoordinates(distance)
        neighbors: list = []
        for coordinate in coordinates:
            target: MeshCode = MeshCode.parse(self.getMeshCode())
            target.shift(coordinate[1], coordinate[0])
            neighbors.append(target)
        return neighbors

    def __calCoordinates(self, distance):
        coordinates = []
        for x in range(-distance, distance + 1, 1):
            for y in range(-distance, distance + 1, 1):
                coordinates.append([x, y])
        return coordinates
