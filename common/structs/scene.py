from proto import MotionInfo, Vector
from pydantic import BaseModel


class Scene(BaseModel):
    plane_id: int = 20411
    floor_id: int = 20411001
    entry_id: int = 2041101


class Position(BaseModel):
    x: int = -26968
    y: int = 78953
    z: int = 14457
    rot_y: int = 11858

    def to_motion_info_proto(self) -> MotionInfo:
        return MotionInfo(
            rot=Vector(y=self.rot_y),
            pos=Vector(
                x=self.x,
                y=self.y,
                z=self.z,
            ),
        )
