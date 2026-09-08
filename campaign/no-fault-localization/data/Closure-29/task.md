Repair a real defect in the Java project Closure (Defects4J bug Closure-29).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.InlineObjectLiteralsTest::testObject10
  - com.google.javascript.jscomp.InlineObjectLiteralsTest::testObject12
  - com.google.javascript.jscomp.InlineObjectLiteralsTest::testObject22
  - com.google.javascript.jscomp.InlineObjectLiteralsTest::testIssue724
  - com.google.javascript.jscomp.IntegrationTest::testIssue724

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.InlineObjectLiteralsTest::testObject10
junit.framework.AssertionFailedError: 
Expected: function local(){var x={};var b=f();x={a:a,b:b};if(x.a)g(x.b)+x.c}
Result: function local(){var JSCompiler_object_inline_a_0;var JSCompiler_object_inline_b_1;var JSCompiler_object_inline_c_2;var b=f();JSCompiler_object_inline_a_0=a,JSCompiler_object_inline_b_1=b,JSCompiler_object_inline_c_2=void 0,true;if(JSCompiler_object_inline_a_0)g(JSCompiler_object_inline_b_1)+JSCompiler_object_inline_c_2}
Node tree inequality:
Tree1:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: expected0] [input_id: InputId: expected0]
        FUNCTION local 1 [source_file: expected0]
            NAME local 1 [source_file: expected0]
            PARAM_LIST 1 [source_file: expected0]
            BLOCK 1 [source_file: expected0]
                VAR 1 [source_file: expected0]
                    NAME x 1 [source_file: expected0]
                        OBJECTLIT 1 [source_file: expected0]
                VAR 1 [source_file: expected0]
                    NAME b 1 [source_file: expected0]
                        CALL 1 [free_call: 1] [source_file: expected0]
                            NAME f 1 [source_file: expected0]
                EXPR_RESULT 1 [source_file: expected0]
                    ASSIGN 1 [source_file: expected0]
                        NAME x 1 [source_file: expected0]
                        OBJECTLIT 1 [source_file: expected0]
                            STRING_KEY a 1 [source_file: expected0]
                                NAME a 1 [source_file: expected0]
                            STRING_KEY b 1 [source_file: expected0]
                                NAME b 1 [source_file: expected0]
                IF 1 [source_file: expected0]
                    GETPROP 1 [source_file: expected0]
                        NAME x 1 [source_file: expected0]
                        STRING a 1 [source_file: expected0]
                    BLOCK 1 [source_file: expected0]
                        EXPR_RESULT 1 [source_file: expected0]
                            ADD 1 [source_file: expected0]
                                CALL 1 [free_call: 1] [source_file: expected0]
                                    NAME g 1 [source_file: expected0]
                                    GETPROP 1 [source_file: expected0]
                                        NAME x 1 [source_file: expected0]
                                        STRING b 1 [source_file: expected0]
                                GETPROP 1 [source_file: expected0]
                                    NAME x 1 [source_file: expected0]
                                    STRING c 1 [source_file: expected0]


Tree2:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: testcode] [input_id: InputId: testcode]
        FUNCTION local 1 [source_file: testcode]
            NAME local 1 [source_file: testcode]
            PARAM_LIST 1 [source_file: testcode]
            BLOCK 1 [source_file: testcode]
                VAR 1 [source_file: testcode]
                    NAME JSCompiler_object_inline_a_0 1 [source_file: testcode]
                VAR 1 [source_file: testcode]
                    NAME JSCompiler_object_inline_b_1 1 [source_file: testcode]
                VAR 1 [source_file: testcode]
                    NAME JSCompiler_object_inline_c_2 1 [source_file: testcode]
                VAR 1 [source_file: testcode]
                    NAME b 1 [source_file: testcode]
                        CALL 1 [free_call: 1] [source_file: testcode]
                            NAME f 1 [source_file: testcode]
                EXPR_RESULT 1 [source_file: testcode]
                    COMMA 1 [source_file: testcode]
                        COMMA 1 [source_file: testcode]
                            COMMA 1 [source_file: testcode]
                                ASSIGN 1 [source_file: testcode]
                                    NAME JSCompiler_object_inline_a_0 1 [source_file: testcode]
                                    NAME a 1 [source_file: testcode]
                                ASSIGN 1 [source_file: testcode]
                                    NAME JSCompiler_object_inline_b_1 1 [source_file: testcode]
                                    NAME b 1 [source_file: testcode]
                            ASSIGN 1 [source_file: testcode]
                                NAME JSCompiler_object_inline_c_2 1 [source_file: testcode]
                                VOID 1 [source_file: testcode]
                                    NUMBER 0.0 1 [source_file: testcode]
                        TRUE 1 [source_file: testcode]
                IF 1 [source_file: testcode]
                    NAME JSCompiler_object_inline_a_0 1 [source_file: testcode]
                    BLOCK 1 [source_file: testcode]
                        EXPR_RESULT 1 [source_file: testcode]
                            ADD 1 [source_file: testcode]
                                CALL 1 [free_call: 1] [source_file: testcode]
                                    NAME g 1 [source_file: testcode]
                                    NAME JSCompiler_object_inline_b_1 1 [source_file: testcode]
                                NAME JSCompiler_object_inline_c_2 1 [source_file: testcode]


Subtree1: BLOCK 1 [source_file: expected0]
    VAR 1 [source_file: expected0]
        NAME x 1 [source_file: expected0]
            OBJECTLIT 1 [source_file: expected0]
    VAR 1 [source_file: expected0]
        NAME b 1 [source_file: expected0]
            CALL 1 [free_call: 1] [source_file: expected0]
                NAME f 1 [source_file: expected0]
    EXPR_RESULT 1 [source_file: expected0]
        ASSIGN 1 [source_file: expected0]
            NAME x 1 [source_file: expected0]
            OBJECTLIT 1 [source_file: expected0]
                STRING_KEY a 1 [source_file: expected0]
                    NAME a 1 [source_file: expected0]
                STRING_KEY b 1 [source_file: expected0]
                    NAME b 1 [source_file: expected0]
    IF 1 [source_file: expected0]
        GETPROP 1 [source_file: expected0]
            NAME x 1 [source_file: expected0]
            STRING a 1 [source_file: expected0]
        BLOCK 1 [source_file: expected0]
            EXPR_RESULT 1 [source_file: expected0]
                ADD 1 [source_file: expected0]
                    CALL 1 [free_call: 1] [source_file: expected0]
                        NAME g 1 [source_file: expected0]
                        GETPROP 1 [source_file: expected0]
                            NAME x 1 [source_file: expected0]
                            STRING b 1 [source_file: expected0]
                    GETPROP 1 [source_file: expected0]
                        NAME x 1 [source_file: expected0]
                        STRING c 1 [source_file: expected0]


Subtree2: BLOCK 1 [source_file: testcode]
    VAR 1 [source_file: testcode]
        NAME JSCompiler_object_inline_a_0 1 [source_file: testcode]
    VAR 1 [source_file: testcode]
        NAME JSCompiler_object_inline_b_1 1 [source_file: testcode]
    VAR 1 [source_file: testcode]
        NAME JSCompiler_object_inline_c_2 1 [source_file: testcode]
    VAR 1 [source_file: testcode]
        NAME b 1 [source_file: testcode]
            CALL 1 [free_call: 1] [source_file: testcode]
                NAME f 1 [source_file: testcode]
    EXPR_RESULT 1 [source_file: testcode]
        COMMA 1 [source_file: testcode]
            COMMA 1 [source_file: testcode]
                COMMA 1 [source_file: testcode]
                    ASSIGN 1 [source_file: testcode]
                        NAME JSCompiler_object_inline_a_0 1 [source_file: testcode]
                        NAME a 1 [source_file: testcode]
                    ASSIGN 1 [source_file: testcode]
                        NAME JSCompiler_object_inline_b_1 1 [source_file: testcode]
                        NAME b 1 [source_file: testcode]
                ASSIGN 1 [source_file: testcode]
                    NAME JSCompiler_object_inline_c_2 1 [source_file: testcode]
                    VOID 1 [source_file: testcode]
                        NUMBER 0.0 1 [source_file: testcode]
            TRUE 1 [source_file: testcode]
    IF 1 [source_file: testcode]
        NAME JSCompiler_object_inline_a_0 1 [source_file: testcode]
        BLOCK 1 [source_file: testcode]
            EXPR_RESULT 1 [source_file: testcode]
                ADD 1 [source_file: testcode]
                    CALL 1 [free_call: 1] [source_file: testcode]
                        NAME g 1 [source_file: testcode]
                        NAME JSCompiler_object_inline_b_1 1 [source_file: testcode]
                    NAME JSCompiler_object_inline_c_2 1 [source_file: testcode]

	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.assertTrue(Assert.java:22)
	at junit.framework.Assert.assertNull(Assert.java:277)
	at junit.framework.TestCase.assertNull(TestCase.java:447)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:892)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:445)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:371)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:340)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:328)
	at com.google.javascript.jscomp.InlineObjectLiteralsTest.testLocal(InlineObjectLiteralsTest.java:355)
	at com.google.javascript.jscomp.InlineObjectLiteralsTest.testObject10(InlineObjectLiteralsTest.java:174)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at junit.framework.TestCase.runTest(TestCase.java:176)
	at junit.framework.TestCase.runBare(TestCase.java:141)
	at junit.framework.TestResult$1.protect(TestResult.java:122)
	at junit.framework.TestResult.runProtected(TestResult.java:142)
	at junit.framework.TestResult.run(TestResult.java:125)
	at junit.framework.TestCase.run(TestCase.java:129)
	at junit.framework.TestSuite.runTest(TestSuite.java:252)
	at junit.framework.TestSuite.run(TestSuite.java:247)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTestRunner.run(JUnitTestRunner.java:520)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeInVM(JUnitTask.java:1492)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:878)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeOrQueue(JUnitTask.java:1980)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:830)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.execute(JUnitTask.java:2287)
	at org.apache.tools.ant.UnknownElement.execute(UnknownElement.java:291)
	at jdk.internal.reflect.GeneratedMethodAccessor4.invoke(Unknown Source)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.apache.tools.ant.dispatch.DispatchUtils.execute(DispatchUtils.java:106)
	at org.apache.tools.ant.Task.perform(Task.java:348)
	at org.apache.tools.ant.Target.execute(Target.java:392)
	at org.apache.tools.ant.Target.performTasks(Target.java:413)
	at org.apache.tools.ant.Project.executeSortedTargets(Project.java:1399)
	at org.apache.tools.ant.Project.executeTarget(Project.java:1368)
	at org.apache.tools.ant.helper.DefaultExecutor.executeTargets(DefaultExecutor.java:41)
	at org.apache.tools.ant.Project.executeTargets(Project.java:1251)
	at org.apache.tools.ant.Main.runBuild(Main.java:811)
	at org.apache.tools.ant.Main.startAnt(Main.java:217)
	at org.apache.tools.ant.launch.Launcher.run(Launcher.java:280)
	at org.apache.tools.ant.
... (truncated)
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
