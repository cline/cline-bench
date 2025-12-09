# Suave HTTP Data Bleeding

During a November 2025 beta testing session, a developer stress-tested their Suave F# web server and watched HTTP responses corrupt in real-time. The httperf tool reported impossible status lines: HTML fragments appearing where HTTP headers should be. "ng-the-package-manager-console">Package Manager" showed up in a status line. A Host header appeared mid-status. Numeric status codes transformed into eight-digit garbage: 1874380688 instead of 200.

This wasn't a simple buffer overflow. Over three days, the Suave team traced it through five commits, each peeling back another layer. First they thought: buffers not clearing. They added Array.Clear everywhere. Still broken. Then: shutdown sequence wrong. They reorganized it. Still broken. Finally, they found it: after serving a file (SocketTask), the lineBuffer wasn't flushing. That was the immediate fix - add one flush() call. But two days later, the real root cause emerged: the lineBuffer was doing double duty, used for both reading HTTP requests AND writing HTTP responses. When you serve a file, write HTML to the buffer, then try to read the next HTTP request from that same buffer, you get exactly what they saw: HTML bleeding into status lines.

The architectural fix separated the buffers - HttpReader gets its own readLineBuffer, Connection has its own lineBuffer. No more sharing. The Terminus agent we tested spent 20 episodes trying to reproduce the bug by hammering an external server, found a spurious 1-byte header difference, and declared victory without touching the code. Comprehensive verification requires checking both fixes: the immediate workaround (flush after SocketTask) and the architectural change (constructor signature). That's the only way to catch agents that solve half the problem.

---

## Technical Details

**The bug:** lineBuffer shared between HttpReader (reading requests) and Connection (writing responses) causes data bleeding under keep-alive + file serving load.

**The fix cascade:**
1. Nov 23: Array.Clear fixes (3 commits) - general buffer safety
2. Nov 24 15:02: flush() after SocketTask (666a370e1f) - immediate workaround
3. Nov 26 11:08: Separate read/write buffers (cd515a10) - architectural fix

**The solution requires:**
1. Add `do! this.Connection.flush()` after SocketTask in HttpOutput.fs
2. Remove `lineBuffer: byte array` parameter from HttpReader constructor
3. HttpReader allocates own `readLineBuffer` from ArrayPool
4. Update Tcp.fs createReader call to not pass lineBuffer

**Verification (4 tests):**
- test_project_compiles: Build succeeds
- test_http_reader_has_separate_buffer: **KEY DISCRIMINATOR** - HttpReader constructor has NO lineBuffer parameter
- test_flush_after_socket_task: SocketTask case includes flush() call
- test_stress_load_completes: httperf stress test shows no corruption

**Repository:** [SuaveIO/suave](https://github.com/SuaveIO/suave) (1337 stars, 15-year history)  
**Broken:** commit `8060f05` (v3.1.0-beta6, Nov 24 2025)  
**Fixed:** commit `cd515a10` (architectural fix, Nov 26 2025)

**Build environment:**
- .NET SDK 9.0+ (requires 9.0.306 per global.json)
- libicu-dev for .NET globalization
- Paket package manager + 60+ dependencies
- httperf for stress testing

**Difficulty:** Medium - Archaeological investigation revealed multi-part fix cascade. Agents must understand HTTP keep-alive semantics, buffer lifecycle, AND recognize the architectural flaw. Test discrimination: Broken state 2/4 (compilation + stress pass), Fixed state 4/4 (all tests pass).