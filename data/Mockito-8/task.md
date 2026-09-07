Repair a real defect in the Java project Mockito (Defects4J bug Mockito-8).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - org.mockito.internal.util.reflection.GenericMetadataSupportTest::typeVariable_of_self_type

Failure output from the initial test run:

```
--- org.mockito.internal.util.reflection.GenericMetadataSupportTest::typeVariable_of_self_type
java.lang.StackOverflowError
	at java.base/sun.reflect.generics.reflectiveObjects.TypeVariableImpl.hashCode(TypeVariableImpl.java:178)
	at java.base/java.util.HashMap.hash(HashMap.java:340)
	at java.base/java.util.HashMap.get(HashMap.java:553)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:182)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActualTypeArgumentFor(GenericMetadataSupport.java:185)
	at org.mockito.internal.util.reflection.GenericMetadataSupport.getActu
... (truncated)
```

Classes the defect is known to be located in:

  - org.mockito.internal.util.reflection.GenericMetadataSupport

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
