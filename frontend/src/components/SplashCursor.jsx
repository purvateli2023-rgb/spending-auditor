import { useEffect, useRef } from "react"

function SplashCursor() {
    const canvasRef = useRef(null)

    useEffect(() => {
        const canvas = canvasRef.current
        const ctx = canvas.getContext("2d")
        let particles = []
        let animationId

        function resize() {
            canvas.width = window.innerWidth
            canvas.height = window.innerHeight
        }
        resize()
        window.addEventListener("resize", resize)

        function addParticle(x, y) {
            particles.push({
                x, y,
                radius: Math.random() * 8 + 4,
                alpha: 0.6,
                color: Math.random() > 0.5 ? "16,185,129" : "52,211,153",
            })
        }

        function handleMove(e) {
            addParticle(e.clientX, e.clientY)
        }
        window.addEventListener("mousemove", handleMove)

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height)
            particles.forEach((p) => {
                ctx.beginPath()
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
                ctx.fillStyle = `rgba(${p.color},${p.alpha})`
                ctx.fill()
                p.radius *= 0.94
                p.alpha *= 0.92
            })
            particles = particles.filter((p) => p.alpha > 0.02)
            animationId = requestAnimationFrame(animate)
        }
        animate()

        return () => {
            window.removeEventListener("mousemove", handleMove)
            window.removeEventListener("resize", resize)
            cancelAnimationFrame(animationId)
        }
    }, [])

    return (
        <canvas
            ref={canvasRef}
            style={{
                position: "fixed",
                top: 0,
                left: 0,
                pointerEvents: "none",
                zIndex: 9999,
            }}
        />
    )
}

export default SplashCursor