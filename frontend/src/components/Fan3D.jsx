
import React, { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, ContactShadows } from "@react-three/drei";
import * as THREE from "three";

const RPM = {
  Off: 0,
  Low: 55,
  Medium: 135,
  High: 260,
};

function Blade({ angle }) {
  const geometry = useMemo(() => {
    const shape = new THREE.Shape();

    shape.moveTo(0.28, -0.13);
    shape.bezierCurveTo(0.75, -0.20, 1.50, -0.28, 2.20, -0.12);
    shape.bezierCurveTo(2.30, -0.02, 2.25, 0.12, 2.10, 0.17);
    shape.bezierCurveTo(1.48, 0.12, 0.85, 0.17, 0.28, 0.13);
    shape.bezierCurveTo(0.22, 0.08, 0.22, -0.07, 0.28, -0.13);

    const geo = new THREE.ExtrudeGeometry(shape, {
      depth: 0.06,
      bevelEnabled: true,
      bevelSegments: 3,
      bevelSize: 0.025,
      bevelThickness: 0.02,
      steps: 1,
      curveSegments: 20,
    });

    geo.rotateX(Math.PI / 2);
    geo.computeVertexNormals();
    return geo;
  }, []);

  return (
    <mesh
      geometry={geometry}
      rotation={[0, angle, 0]}
      castShadow
      receiveShadow
    >
      <meshPhysicalMaterial
        color="#a57448"
        roughness={0.4}
        clearcoat={0.35}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

function FanModel({ speed }) {
  const rotor = useRef();
  const rpm = useRef(0);

  useFrame((_, delta) => {
    rpm.current = THREE.MathUtils.damp(
      rpm.current,
      RPM[speed] ?? 0,
      1.3,
      delta
    );

    if (rotor.current) {
      rotor.current.rotation.y +=
        rpm.current * Math.PI * 2 / 60 * delta;
    }
  });

  return (
    <group scale={1.3}>

      {/* Ceiling canopy */}
      <mesh position={[0, 0.95, 0]} castShadow>
        <cylinderGeometry args={[0.26, 0.34, 0.18, 48]} />
        <meshStandardMaterial
          color="#17191d"
          metalness={0.85}
          roughness={0.22}
        />
      </mesh>

      {/* Downrod */}
      <mesh position={[0, 0.50, 0]} castShadow>
        <cylinderGeometry args={[0.07, 0.07, 0.75, 32]} />
        <meshStandardMaterial
          color="#25282d"
          metalness={0.9}
          roughness={0.2}
        />
      </mesh>

      {/* Upper motor */}
      <mesh position={[0, 0.12, 0]} castShadow>
        <cylinderGeometry args={[0.40, 0.36, 0.32, 64]} />
        <meshPhysicalMaterial
          color="#202329"
          metalness={0.85}
          roughness={0.23}
        />
      </mesh>

      {/* Lower motor */}
      <mesh position={[0, -0.20, 0]} castShadow>
        <cylinderGeometry args={[0.32, 0.39, 0.30, 64]} />
        <meshPhysicalMaterial
          color="#111317"
          metalness={0.8}
          roughness={0.23}
        />
      </mesh>

      {/* Gold motor ring */}
      <mesh position={[0, -0.36, 0]}>
        <torusGeometry args={[0.30, 0.02, 16, 64]} />
        <meshStandardMaterial
          color="#c7a35a"
          metalness={0.95}
          roughness={0.18}
        />
      </mesh>

      {/* Rotating blades and arms */}
      <group ref={rotor}>
        {[0, 1, 2].map((i) => (
          <group
            key={i}
            rotation={[0, i * Math.PI * 2 / 3, 0]}
          >
            <Blade angle={0} />

            <mesh position={[0.42, -0.015, 0]} castShadow>
              <boxGeometry args={[0.50, 0.075, 0.15]} />
              <meshStandardMaterial
                color="#25282d"
                metalness={0.75}
                roughness={0.25}
              />
            </mesh>
          </group>
        ))}
      </group>

      {/* Center cap */}
      <mesh position={[0, -0.40, 0]}>
        <cylinderGeometry args={[0.16, 0.19, 0.09, 48]} />
        <meshPhysicalMaterial
          color="#111317"
          metalness={0.85}
          roughness={0.2}
        />
      </mesh>

      {/* Gold accent */}
      <mesh position={[0, -0.455, 0]}>
        <torusGeometry args={[0.11, 0.012, 12, 48]} />
        <meshStandardMaterial
          color="#c7a35a"
          metalness={0.9}
          roughness={0.2}
        />
      </mesh>

    </group>
  );
}

export default function Fan3D({ speed = "Off" }) {
  return (
    <div className="fan3d-container">
      <Canvas
        shadows
        camera={{
          position: [4, -7, 3.5],
          fov: 38,
          up: [0, 1, 0],
        }}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
        }}
        dpr={[1, 1.5]}
      >
        <color attach="background" args={["#f5f3ed"]} />

        <ambientLight intensity={0.9} />

        <directionalLight
          position={[4, -4, 6]}
          intensity={2.5}
          castShadow
          shadow-mapSize={[1024, 1024]}
        />

        <directionalLight
          position={[-4, 3, 4]}
          intensity={1.4}
          color="#fff0d4"
        />

        <pointLight
          position={[0, -2, 3]}
          intensity={0.8}
          color="#d8b878"
        />

        <FanModel speed={speed} />

        <ContactShadows
          position={[0, -0.8, 0]}
          opacity={0.15}
          scale={6}
          blur={3}
          far={4}
        />

        <Environment preset="studio" />
      </Canvas>
    </div>
  );
}
