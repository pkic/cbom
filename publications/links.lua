-- Rewrites relative links to the tagged release on GitHub.
-- Links in the Markdown are written relative to publications/src/.
-- The tag is set by the build script through the CBOM_TAG variable.
local base = "https://github.com/pkic/cbom/blob/" .. (os.getenv("CBOM_TAG") or "release-1") .. "/"

local function normalise(path)
  local parts = {}
  for part in ("publications/src/" .. path):gmatch("[^/]+") do
    if part == ".." then table.remove(parts)
    elseif part ~= "." then table.insert(parts, part) end
  end
  return table.concat(parts, "/")
end

function Link(el)
  local t = el.target
  if t:match("^%a[%w+.-]*:") or t:match("^#") or t:match("^mailto:") then
    return el
  end
  el.target = base .. normalise(t)
  return el
end
