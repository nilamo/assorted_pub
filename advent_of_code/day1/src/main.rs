
enum Direction {
    North, South, East, West
}

struct Coord {
    x: i32,
    y: i32
}

impl Direction {
    fn next(&self, turn: &str) -> Direction {
        let right = "R" == turn;

        match self {
            &Direction::North => if right { Direction::East } else { Direction::West },
            &Direction::East => if right { Direction::South } else { Direction::North },
            &Direction::South => if right { Direction::West } else { Direction::East },
            &Direction::West => if right { Direction::North } else { Direction::South }
        }
    }
}

impl Coord {
    fn walk(&self, facing: &Direction, distance: i32) -> Coord {
        match facing {
            &Direction::North => Coord { y: self.y + distance, x: self.x },
            &Direction::South => Coord { y: self.y - distance, x: self.x },
            &Direction::East => Coord { y: self.y, x: self.x + distance },
            &Direction::West => Coord { y: self.y, x: self.x - distance },
        }
    }
}

fn main() {
    let buffer = "R2, L3"; // output is 5
    let buffer = "R2, R2, R2"; // output is 2
    let buffer = "R5, L5, R5, R3"; // output is 12

    let steps = buffer.trim().split(",").map(|x| x.trim().to_string());
    let mut direction = Direction::North;
    let mut pos = Coord { y: 0, x: 0 };

    for step in steps {
        let (dir, dist) = step.split_at(1);
        let dist: i32 = dist.parse().unwrap();

        direction = direction.next(dir);
        pos = pos.walk(&direction, dist);
    }

    println!("{}+{}={}", pos.y, pos.x, (pos.y+pos.x).abs());
}
