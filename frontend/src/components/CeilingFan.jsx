
import { useEffect, useRef, useState } from "react";
import "./CeilingFan.css";

const SPEEDS = {
  Off: 0,
  Low: 1.2,
  Medium: 2.5,
  High: 4.5,
};

export default function CeilingFan({ speed = "Off" }) {
  const targetSpeed = SPEEDS[speed] ?? 0;

  const [rotationSpeed, setRotationSpeed] = useState(0);
  const angleRef = useRef(0);
  const speedRef = useRef(0);
  const frameRef = useRef(null);
  const previousTimeRef = useRef(null);

  useEffect(() => {
    const animate = (time) => {
      if (previousTimeRef.current === null) {
        previousTimeRef.current = time;
      }

      const delta = Math.min(
        (time - previousTimeRef.current) / 1000,
        0.05
      );

      previousTimeRef.current = time;

      // Smooth acceleration and deceleration
      const acceleration = 1.1;
      const difference = targetSpeed - speedRef.current;

      speedRef.current +=
        Math.sign(difference) *
        Math.min(Math.abs(difference), acceleration * delta);

      // Continuous rotation
      angleRef.current =
        (angleRef.current + speedRef.current * delta * 360) % 360;

      setRotationSpeed(speedRef.current);

      frameRef.current = requestAnimationFrame(animate);
    };

    frameRef.current = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(frameRef.current);
      previousTimeRef.current = null;
    };
  }, [targetSpeed]);

  const isRunning = rotationSpeed > 0.03;

  const simulatedRPM = Math.round(rotationSpeed * 60);

  return (
    <div className="atom-fan-stage">
      {/* Ceiling */}
      <div className="atom-ceiling" />

      {/* Suspension */}
      <div className="atom-suspension">
        <div className="atom-canopy">
          <div className="canopy-highlight" />
        </div>

        <div className="atom-downrod" />

        {/* Motor housing */}
        <div className="atom-motor">
          <div className="motor-top" />
          <div className="motor-body">
            <div className="motor-highlight" />
            <div className="motor-band" />
            <div className="motor-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>

          {/* Rotor and blades */}
          <div
            className="atom-rotor"
            style={{
              transform: `rotate(${angleRef.current}deg)`,
            }}
          >
            {[0, 120, 240].map((angle) => (
              <div
                key={angle}
                className="atom-blade"
                style={{
                  transform: `rotate(${angle}deg)`,
                }}
              >
                <div className="blade-wood-grain" />
                <div className="blade-highlight" />
                <div className="blade-tip" />
              </div>
            ))}
          </div>

          {/* Central rotor cap */}
          <div className="atom-center">
            <div className="center-ring" />
            <div className="center-dot" />
          </div>
        </div>
      </div>

      {/* Floor shadow */}
      <div
        className="atom-floor-shadow"
        style={{
          opacity: isRunning ? 0.16 : 0.09,
        }}
      />

      {/* Status */}
      <div className="atom-fan-status">
        <span className={`atom-status-light ${isRunning ? "on" : "off"}`} />

        <span className="atom-status-label">
          {isRunning ? `${speed.toUpperCase()} SPEED` : "FAN OFF"}
        </span>

        <span className="atom-status-divider" />

        <span className="atom-rpm">
          {simulatedRPM} RPM
        </span>
      </div>
    </div>
  );
}
