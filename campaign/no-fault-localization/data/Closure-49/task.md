Repair a real defect in the Java project Closure (Defects4J bug Closure-49).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.FunctionInjectorTest::testInline19b
  - com.google.javascript.jscomp.FunctionInjectorTest::testInlineIntoLoop
  - com.google.javascript.jscomp.FunctionInjectorTest::testInline13
  - com.google.javascript.jscomp.FunctionInjectorTest::testInline14
  - com.google.javascript.jscomp.FunctionInjectorTest::testInline15
  - com.google.javascript.jscomp.FunctionInjectorTest::testInline16
  - com.google.javascript.jscomp.FunctionInjectorTest::testInline17
  - com.google.javascript.jscomp.FunctionInjectorTest::testInline18
  - com.google.javascript.jscomp.FunctionInjectorTest::testInline19
  - com.google.javascript.jscomp.FunctionInjectorTest::testBug1897706
  - com.google.javascript.jscomp.FunctionInjectorTest::testInlineFunctionWithInnerFunction5
  - com.google.javascript.jscomp.FunctionToBlockMutatorTest::testMutateWithParameters3
  - com.google.javascript.jscomp.FunctionToBlockMutatorTest::testMutateCallInLoopVars1
  - com.google.javascript.jscomp.FunctionToBlockMutatorTest::testMutateInitializeUninitializedVars1
  - com.google.javascript.jscomp.FunctionToBlockMutatorTest::testMutateInitializeUninitializedVars2
  - com.google.javascript.jscomp.FunctionToBlockMutatorTest::testMutateFunctionDefinition
  - com.google.javascript.jscomp.FunctionToBlockMutatorTest::testMutate8
  - com.google.javascript.jscomp.InlineFunctionsTest::testLoopWithFunctionWithFunction
  - com.google.javascript.jscomp.InlineFunctionsTest::testShadowVariables16
  - com.google.javascript.jscomp.InlineFunctionsTest::testShadowVariables18
  - com.google.javascript.jscomp.InlineFunctionsTest::testCostBasedInlining11
  - com.google.javascript.jscomp.InlineFunctionsTest::testMixedModeInliningCosting3
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineNeverMutateConstants
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineWithThis7
  - com.google.javascript.jscomp.InlineFunctionsTest::testAnonymous1
  - com.google.javascript.jscomp.InlineFunctionsTest::testAnonymous3
  - com.google.javascript.jscomp.InlineFunctionsTest::testShadowVariables1
  - com.google.javascript.jscomp.InlineFunctionsTest::testShadowVariables3
  - com.google.javascript.jscomp.InlineFunctionsTest::testShadowVariables6
  - com.google.javascript.jscomp.InlineFunctionsTest::testShadowVariables7
  - com.google.javascript.jscomp.InlineFunctionsTest::testFunctionExpressionCallInlining11b
  - com.google.javascript.jscomp.InlineFunctionsTest::testComplexInlineNoResultNoParamCall3
  - com.google.javascript.jscomp.InlineFunctionsTest::testCostBasedInlining9
  - com.google.javascript.jscomp.InlineFunctionsTest::testMethodWithFunctionWithFunction
  - com.google.javascript.jscomp.InlineFunctionsTest::testFunctionExpressionYCombinator
  - com.google.javascript.jscomp.InlineFunctionsTest::testComplexInlineVars7
  - com.google.javascript.jscomp.InlineFunctionsTest::testComplexFunctionWithFunctionDefinition2a
  - com.google.javascript.jscomp.InlineFunctionsTest::testComplexInline7
  - com.google.javascript.jscomp.InlineFunctionsTest::testFunctionExpressionOmega
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions15b
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions15d
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions16a
  - com.google.javascript.jscomp.InlineFunctionsTest::testBug4944818
  - com.google.javascript.jscomp.InlineFunctionsTest::testComplexSample
  - com.google.javascript.jscomp.InlineFunctionsTest::testNoInlineIfParametersModified1
  - com.google.javascript.jscomp.InlineFunctionsTest::testNoInlineIfParametersModified2
  - com.google.javascript.jscomp.InlineFunctionsTest::testNoInlineIfParametersModified3
  - com.google.javascript.jscomp.InlineFunctionsTest::testNoInlineIfParametersModified4
  - com.google.javascript.jscomp.InlineFunctionsTest::testNoInlineIfParametersModified5
  - com.google.javascript.jscomp.InlineFunctionsTest::testNoInlineIfParametersModified6
  - com.google.javascript.jscomp.InlineFunctionsTest::testNoInlineIfParametersModified7
  - com.google.javascript.jscomp.InlineFunctionsTest::testIssue423
  - com.google.javascript.jscomp.InlineFunctionsTest::testComplexFunctionWithFunctionDefinition2
  - com.google.javascript.jscomp.InlineFunctionsTest::testComplexFunctionWithFunctionDefinition3
  - com.google.javascript.jscomp.InlineFunctionsTest::testDecomposeFunctionExpressionInCall
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineNeverOverrideNewValues
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineBlockMutableArgs1
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineBlockMutableArgs2
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineBlockMutableArgs3
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineBlockMutableArgs4
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions10
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions13
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions22
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions23
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions9
  - com.google.javascript.jscomp.MakeDeclaredNamesUniqueTest::testMakeLocalNamesUniqueWithContext5

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.FunctionInjectorTest::testInline19b
junit.framework.AssertionFailedError: 
Expected: var x=1;var y=2;function foo(a,b){y=a;x=b}function bar(){var b$$inline_1=y;y=x;x=b$$inline_1}
Result: var x=1;var y=2;function foo(a,b){y=a;x=b}function bar(){var b$$inline_3=y;y=x;x=b$$inline_3}
Node tree inequality:
Tree1:
SCRIPT 1 [synthetic: 1] [source_file:  [testcode] ] [input_id: InputId:  [testcode] ]
    VAR 1 [source_file:  [testcode] ]
        NAME x 1 [source_file:  [testcode] ]
            NUMBER 1.0 1 [source_file:  [testcode] ]
    VAR 1 [source_file:  [testcode] ]
        NAME y 1 [source_file:  [testcode] ]
            NUMBER 2.0 1 [source_file:  [testcode] ]
    FUNCTION foo 1 [source_file:  [testcode] ]
        NAME foo 1 [source_file:  [testcode] ]
        LP 1 [source_file:  [testcode] ]
            NAME a 1 [source_file:  [testcode] ]
            NAME b 1 [source_file:  [testcode] ]
        BLOCK 1 [source_file:  [testcode] ]
            EXPR_RESULT 1 [source_file:  [testcode] ]
                ASSIGN 1 [source_file:  [testcode] ]
                    NAME y 1 [source_file:  [testcode] ]
                    NAME a 1 [source_file:  [testcode] ]
            EXPR_RESULT 1 [source_file:  [testcode] ]
                ASSIGN 1 [source_file:  [testcode] ]
                    NAME x 1 [source_file:  [testcode] ]
                    NAME b 1 [source_file:  [testcode] ]
    EMPTY 1 [source_file:  [testcode] ]
    FUNCTION bar 1 [source_file:  [testcode] ]
        NAME bar 1 [source_file:  [testcode] ]
        LP 1 [source_file:  [testcode] ]
        BLOCK 1 [source_file:  [testcode] ]
            BLOCK 1 [source_file:  [testcode] ]
                VAR 1 [source_file:  [testcode] ]
                    NAME b$$inline_1 1 [source_file:  [testcode] ]
                        NAME y 1 [source_file:  [testcode] ]
                EXPR_RESULT 1 [source_file:  [testcode] ]
                    ASSIGN 1 [source_file:  [testcode] ]
                        NAME y 1 [source_file:  [testcode] ]
                        NAME x 1 [source_file:  [testcode] ]
                EXPR_RESULT 1 [source_file:  [testcode] ]
                    ASSIGN 1 [source_file:  [testcode] ]
                        NAME x 1 [source_file:  [testcode] ]
                        NAME b$$inline_1 1 [source_file:  [testcode] ]


Tree2:
SCRIPT 1 [synthetic: 1] [source_file: code] [input_id: InputId: code]
    VAR 1 [source_file: code]
        NAME x 1 [source_file: code]
            NUMBER 1.0 1 [source_file: code]
    VAR 1 [source_file: code]
        NAME y 1 [source_file: code]
            NUMBER 2.0 1 [source_file: code]
    FUNCTION foo 1 [source_file: code]
        NAME foo 1 [source_file: code]
        LP 1 [source_file: code]
            NAME a 1 [source_file: code]
            NAME b 1 [source_file: code]
        BLOCK 1 [source_file: code]
            EXPR_RESULT 1 [source_file: code]
                ASSIGN 1 [source_file: code]
                    NAME y 1 [source_file: code]
                    NAME a 1 [source_file: code]
            EXPR_RESULT 1 [source_file: code]
                ASSIGN 1 [source_file: code]
                    NAME x 1 [source_file: code]
                    NAME b 1 [source_file: code]
    EMPTY 1 [source_file: code]
    FUNCTION bar 1 [source_file: code]
        NAME bar 1 [source_file: code]
        LP 1 [source_file: code]
        BLOCK 1 [source_file: code]
            BLOCK 1 [source_file: code]
                VAR 1 [source_file: code]
                    NAME b$$inline_3 1 [source_file: code]
                        NAME y 1 [source_file: code]
                EXPR_RESULT 1 [source_file: code]
                    ASSIGN 1 [source_file: code]
                        NAME y 1 [source_file: code]
                        NAME x 1 [source_file: code]
                EXPR_RESULT 1 [source_file: code]
                    ASSIGN 1 [source_file: code]
                        NAME x 1 [source_file: code]
                        NAME b$$inline_3 1 [source_file: code]


Subtree1: NAME b$$inline_1 1 [source_file:  [testcode] ]
    NAME y 1 [source_file:  [testcode] ]


Subtree2: NAME b$$inline_3 1 [source_file: code]
    NAME y 1 [source_file: code]

	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.assertTrue(Assert.java:22)
	at junit.framework.Assert.assertNull(Assert.java:277)
	at com.google.javascript.jscomp.FunctionInjectorTest$2.call(FunctionInjectorTest.java:1479)
	at com.google.javascript.jscomp.FunctionInjectorTest$TestCallback.visit(FunctionInjectorTest.java:1524)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:498)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:491)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:491)
	at com.google.javascript.jscomp.NodeTraversal.traverseFunction(NodeTraversal.java:536)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:483)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:491)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:491)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:277)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:455)
	at com.google.javascript.jscomp.FunctionInjectorTest.helperInlineReferenceToFunction(FunctionInjectorTest.java:1488)
	at com.google.javascript.jscomp.FunctionInjectorTest.helperInlineReferenceToFunction(FunctionInjectorTest.java:1393)
	at com.google.javascript.jscomp.FunctionInjectorTest.testInline19b(FunctionInjectorTest.java:945)
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
	at org.apache.tools.ant.launch.Launcher.main(Launcher.java:109)
--- com.google.javascript.jscomp.FunctionInjectorTest::testInlineIntoLoop
junit.framework.AssertionFailedError: 
Expected: function foo(a){var b;return a}for(;1;){var b$$inline_1=void 0;1}
Result: function foo(a){var b;return a}for(;1;){var b$$inline_3=void 0;1}
Node tree inequality:
Tree1:
SCRIPT 1 [synthetic: 1] [source_file:  [testcode] ] [input_id: InputId:  [testcode] ]
    FUNCTION foo 1 [source_file:  [testcode] ]
        NAME foo 1 [source_file:  [testcode] ]
        LP 1 [source_file:  [testcode] ]
            NAME a 1 [source_file:  [testcode] ]
        BLOCK 1 [source_file:  [testcode] ]
            VAR 1 [source_file:  [testcode] ]
                NAME b 1 [source_file:  [testcode] ]
            RETURN 1 [source_file:  [testcode] ]
                NAME a 1 [source_file:  [testcode] ]
    EMPTY 1 [source_file:  [testcode] ]
    FOR 1 [source_file:  [testcode] ]
        EMPTY 1 [source_file:  [testcode] ]
        NUMBER 1.0 1 [source_file:  [testcode] ]
        EMPTY 1 [source_file:  [testcode] ]
        BLOCK 1 [source_file:  [testcode] ]
            BLOCK 1 [source_file:  [testcode] ]
                VAR 1 [source_file:  [testcode] ]
                    NAME b$$inline_1 1 [source_file:  [testcode] ]
                        VOID 1 [source_file:  [testcode] ]
                            NUMBER 0.0 1 [source_file:  [testcode] ]
                EXPR_RESULT 1 [source_file:  [testcode] ]
                    NUMBER 1.0 1 [source_file:  [testcode] ]


Tree2:
SCRIPT 1 [synthetic: 1] [source_file: code] [input_id: InputId: code]
    FUNCTION foo 1 [source_file: code]
        NAME foo 1 [source_file: code]
        LP 1 [source_file: code]
            NAME a 1 [source_file: code]
        BLOCK 1 [source_file: code]
            VAR 1 [source_file: code]
                NAME b 1 [source_file: code]
            RETURN 1 [source_file: code]
                NAME a 1 [source_file: code]
    EMPTY 1 [source_file: code]
    FOR 1 [source_file: code]
        EMPTY 1 [source_file: code]
        NUMBER 1.0 1 [source_file: code]
        EMPTY 1 [source_file: code]
        BLOCK 1 [source_file: code]
            BLOCK 1 [source_file: code]
                VAR 1 [source_file: code]
                    NAME b$$inline_3 1 [source_file: code]
                        VOID 1 [source_file: code]
                            NUMBER 0.0 1 [source_file: code]
                EXPR_RESULT 1 [source_file: code]
                    NUMBER 1.0 1 [source_file: code]


Subtree1: NAME b$$inline_1 1 [source_file:  [testcode] ]
    VOID 1 [source_file:  [testcode] ]
        NUMBER 0.0 1 [source_file:  [testcode] ]


Subtree2: NAME b$$inline_3 1 [source_file: code]
    VOID 1 [source_file: code]
        NUMBER 0.0 1 [source_file: code]

	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.assertTrue(Assert.java:22)
	at junit.framework.Assert.assertNull(Assert.java:277)
	at com.google.javascript.jscomp.FunctionInjectorTest$2.call(FunctionInjectorTest.java:1479)
	at com.google.javascript.jscomp.FunctionInjectorTest$TestCallback.visit(FunctionInjectorTest.java:1524)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:498)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:491)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:491)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:491)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:491)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:491)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:277)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:455)
	at com.google.javascript.jscomp.FunctionInjectorTest.he
... (truncated)
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
