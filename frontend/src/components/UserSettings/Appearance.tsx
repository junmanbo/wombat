import { Container, Heading, Stack } from "@chakra-ui/react"
import { useTheme } from "next-themes"

import { Radio, RadioGroup } from "@/components/ui/radio"

const Appearance = () => {
  const { theme, setTheme } = useTheme()

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          테마 설정
        </Heading>

        <RadioGroup
          onValueChange={(e) => e.value && setTheme(e.value)}
          value={theme}
          colorPalette="teal"
        >
          <Stack>
            <Radio value="system">시스템 설정</Radio>
            <Radio value="light">라이트 모드</Radio>
            <Radio value="dark">다크 모드</Radio>
          </Stack>
        </RadioGroup>
      </Container>
    </>
  )
}
export default Appearance
