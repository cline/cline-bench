"""
Comprehensive tests for Suave HTTP data bleeding fix.

Tests verify BOTH parts of the complete fix cascade:
1. Immediate workaround: flush() after SocketTask (666a370e1f)
2. Architectural fix: Separate read/write buffers (cd515a10)

This provides strong discrimination between broken and fixed states.
"""

import subprocess
import re


def test_project_compiles():
    """
    Verify Suave compiles successfully.
    """
    result = subprocess.run(
        ["dotnet", "build", "Suave.sln"],
        cwd="/app",
        capture_output=True,
        text=True,
        timeout=180
    )
    
    assert result.returncode == 0, f"Build failed: {result.stderr}"


def test_http_reader_has_separate_buffer():
    """
    ARCHITECTURAL FIX TEST (cd515a10): Verify HttpReader uses separate buffer.
    
    The root cause: lineBuffer was shared between HttpReader (reading requests)
    and Connection (writing responses). This caused HTML response data to bleed
    into HTTP request line parsing.
    
    The architectural fix (cd515a10, Nov 26): HttpReader allocates its own
    readLineBuffer instead of sharing Connection's lineBuffer.
    
    **BROKEN STATE (8060f05):**
    type HttpReader(transport, lineBuffer: byte array, pipe, cancellationToken)
                                ^^^^^^^^^^^^^^^^^^^ - SHARED buffer parameter
    
    **FIXED STATE (cd515a10):**
    type HttpReader(transport, pipe, cancellationToken)
                    - NO lineBuffer parameter! Uses internal readLineBuffer.
    
    This test DISCRIMINATES: Broken has parameter, fixed doesn't.
    """
    with open("/app/src/Suave/Sockets/HttpReader.fs", "r") as f:
        content = f.read()
    
    # Find the HttpReader type constructor
    constructor_match = re.search(
        r'type\s+HttpReader\s*\([^)]+\)',
        content
    )
    
    assert constructor_match is not None, "Could not find HttpReader type definition"
    
    constructor = constructor_match.group(0)
    
    # The FIX: HttpReader should NOT take lineBuffer as parameter
    # It should allocate its own readLineBuffer internally
    assert "lineBuffer" not in constructor, (
        f"HttpReader constructor should NOT take 'lineBuffer' as parameter.\n\n"
        f"ROOT CAUSE: Sharing lineBuffer between HttpReader (read) and Connection (write) "
        f"caused data bleeding. When SocketTask wrote file data to lineBuffer, HttpReader "
        f"would read that HTML when parsing the next HTTP request line.\n\n"
        f"ARCHITECTURAL FIX (cd515a10): HttpReader allocates its own readLineBuffer, "
        f"Connection has separate lineBuffer for writes. No more sharing.\n\n"
        f"Found constructor: {constructor}\n\n"
        f"Expected: type HttpReader(transport: ITransport, pipe: Pipe, cancellationToken)\n"
        f"(No lineBuffer parameter)"
    )
    
    # Verify HttpReader allocates its own buffer internally
    # Should have: let readLineBuffer = ArrayPool.Shared.Rent(...)
    assert "readLineBuffer" in content, (
        "HttpReader should allocate its own readLineBuffer internally. "
        "Look for: let readLineBuffer = ArrayPool<byte>.Shared.Rent(...)"
    )


def test_flush_after_socket_task():
    """
    IMMEDIATE FIX TEST (666a370e1f): Verify flush() after SocketTask.
    
    The immediate workaround (Nov 24): Add flush() after SocketTask completes
    to clear lineBuffer before connection reuse.
    
    This prevents file transfer data from bleeding into next request,
    even while lineBuffer was still shared (before architectural fix).
    """
    with open("/app/src/Suave/HttpOutput.fs", "r") as f:
        content = f.read()
    
    # Find SocketTask case in writeContent method
    socket_task_match = re.search(
        r'\|\s*SocketTask\s+f\s*->\s*task\s*\{[^}]*\}',
        content,
        re.DOTALL
    )
    
    assert socket_task_match is not None, (
        "Could not find SocketTask case in HttpOutput.fs writeContent method"
    )
    
    socket_task_code = socket_task_match.group(0)
    
    # Verify flush() is called after SocketTask function
    assert "flush()" in socket_task_code, (
        f"SocketTask case must call flush() after file transfer.\n\n"
        f"BUG: SocketTask serves file without flushing lineBuffer, causing "
        f"data to bleed into subsequent keep-alive requests.\n\n"
        f"FIX: Add 'do! this.Connection.flush()' after SocketTask completes.\n\n"
        f"Found SocketTask code:\n{socket_task_code}"
    )
    
    # Verify flush comes AFTER the function call
    # Pattern: do! f (...) followed by do! flush()
    flush_after = re.search(
        r'do!\s+f\s*\([^)]+\).*?do!\s+.*?flush\(\)',
        socket_task_code,
        re.DOTALL
    )
    
    assert flush_after is not None, (
        "flush() must be called AFTER SocketTask function completes. "
        "Order matters: file transfer first, THEN flush."
    )


def test_stress_load_completes():
    """
    BEHAVIORAL TEST: Verify stress test completes without httperf errors.
    
    While the race condition is too rare to reproduce reliably, we verify
    the stress test runs cleanly with file serving.
    """
    import os
    import time
    
    # Create test file
    os.makedirs("/app/test-files", exist_ok=True)
    with open("/app/test-files/test.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><h1>Package Manager</h1><p>Host: 20.228.142.233</p></body>
</html>
""")
    
    # Create server
    with open("/app/test-server.fsx", "w") as f:
        f.write("""
#r "/app/src/Suave/bin/Debug/net9.0/Suave.dll"
open Suave
open Suave.Files
let config = { defaultConfig with 
    bindings = [HttpBinding.createSimple HTTP "127.0.0.1" 8083]
    homeFolder = Some "/app/test-files" }
startWebServer config Files.browseHome
""")
    
    server = subprocess.Popen(
        ["dotnet", "fsi", "/app/test-server.fsx"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/app"
    )
    
    try:
        time.sleep(5)
        
        result = subprocess.run(
            ["httperf", "--server=127.0.0.1", "--port=8083", 
             "--uri=/test.html", "--rate=20", "--num-conns=10",
             "--num-calls=100", "--burst-length=10"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        invalid = output.count("invalid status line")
        bad = output.count("bad status")
        
        assert invalid == 0 and bad == 0, (
            f"httperf detected corruption: {invalid} invalid, {bad} bad status"
        )
        
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()